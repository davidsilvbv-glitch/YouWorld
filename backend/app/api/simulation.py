"""
Rutas de API relacionadas con simulaciÃ³n
Paso 2: Lectura y filtrado de entidades Zep, preparaciÃ³n y ejecuciÃ³n de simulaciÃ³n OASIS (automatizaciÃ³n completa)
"""

import os
import traceback
from flask import request, jsonify, send_file

from . import simulation_bp
from ..config import Config
from ..memory import get_memory_backend, FilteredEntities
from ..services.zep_entity_reader import ZepEntityReader
from ..services.oasis_profile_generator import OasisProfileGenerator
from ..services.simulation_manager import SimulationManager, SimulationStatus
from ..services.simulation_runner import SimulationRunner, RunnerStatus
from ..utils.logger import get_logger
from ..utils.locale import t, get_locale, set_locale
from ..models.project import ProjectManager
from ..auth import bind_simulation_to_user, get_current_user, get_user_simulation_ids, user_owns_project, user_owns_simulation

logger = get_logger("mirofish.api.simulation")


# Prefijo de optimizaciÃ³n de prompt de Interview
# Agregar este prefijo evita que el Agent invoque herramientas, responda directamente con texto
INTERVIEW_PROMPT_PREFIX = "Combinando tu persona, todos los recuerdos y acciones pasados, no invoques ninguna herramienta y respÃ³ndeme directamente con texto:"


def optimize_interview_prompt(prompt: str) -> str:
    """
    Optimizar preguntas de Interview, agregar prefijo para evitar que Agent invoque herramientas

    Args:
        prompt: Pregunta original

    Returns:
        Pregunta optimizada
    """
    if not prompt:
        return prompt
    # Evitar agregar prefijo repetidamente
    if prompt.startswith(INTERVIEW_PROMPT_PREFIX):
        return prompt
    return f"{INTERVIEW_PROMPT_PREFIX}{prompt}"


# ============== Interfaces de lectura de entidades ==============


@simulation_bp.route("/entities/<graph_id>", methods=["GET"])
def get_graph_entities(graph_id: str):
    """
    Obtener todas las entidades del grafo (filtradas)

    Solo retorna nodos que cumplen con tipos de entidades predefinidos (Labels que no sean solo Entity)

    ParÃ¡metros Query:
        entity_types: Lista de tipos de entidades separados por coma (opcional, para filtrado adicional)
        enrich: Si obtener informaciÃ³n de bordes relacionada (por defecto true)
    """
    try:
        if not Config.ZEP_API_KEY:
            return jsonify({"success": False, "error": t("api.zepApiKeyMissing")}), 500

        entity_types_str = request.args.get("entity_types", "")
        entity_types = (
            [t.strip() for t in entity_types_str.split(",") if t.strip()]
            if entity_types_str
            else None
        )
        enrich = request.args.get("enrich", "true").lower() == "true"

        logger.info(
            f"Obtener entidades del grafo: graph_id={graph_id}, entity_types={entity_types}, enrich={enrich}"
        )

        reader = ZepEntityReader()
        result = reader.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=entity_types,
            enrich_with_edges=enrich,
        )

        return jsonify({"success": True, "data": result.to_dict()})

    except Exception as e:
        logger.error(f"Error al obtener entidad del grafo: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/entities/<graph_id>/<entity_uuid>", methods=["GET"])
def get_entity_detail(graph_id: str, entity_uuid: str):
    """Obtener detalles de una entidad individual"""
    try:
        if not Config.ZEP_API_KEY:
            return jsonify({"success": False, "error": t("api.zepApiKeyMissing")}), 500

        reader = ZepEntityReader()
        entity = reader.get_entity_with_context(graph_id, entity_uuid)

        if not entity:
            return jsonify(
                {"success": False, "error": t("api.entityNotFound", id=entity_uuid)}
            ), 404

        return jsonify({"success": True, "data": entity.to_dict()})

    except Exception as e:
        logger.error(f"Error al obtener detalles de entidad: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/entities/<graph_id>/by-type/<entity_type>", methods=["GET"])
def get_entities_by_type(graph_id: str, entity_type: str):
    """Obtener todas las entidades de un tipo especÃ­fico"""
    try:
        if not Config.ZEP_API_KEY:
            return jsonify({"success": False, "error": t("api.zepApiKeyMissing")}), 500

        enrich = request.args.get("enrich", "true").lower() == "true"

        reader = ZepEntityReader()
        entities = reader.get_entities_by_type(
            graph_id=graph_id, entity_type=entity_type, enrich_with_edges=enrich
        )

        return jsonify(
            {
                "success": True,
                "data": {
                    "entity_type": entity_type,
                    "count": len(entities),
                    "entities": [e.to_dict() for e in entities],
                },
            }
        )

    except Exception as e:
        logger.error(f"Error al obtener entidad: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


# ============== Interfaces de gestiÃ³n de simulaciÃ³n ==============


@simulation_bp.route("/create", methods=["POST"])
def create_simulation():
    """
    Crear nueva simulación
    """
    try:
        data = request.get_json() or {}

        project_id = data.get("project_id")
        if not project_id:
            return jsonify({"success": False, "error": t("api.requireProjectId")}), 400

        current_user = get_current_user()
        if current_user and not user_owns_project(current_user.user_id, project_id):
            return jsonify({"success": False, "error": "forbidden"}), 403

        project = ProjectManager.get_project(project_id)
        if not project:
            return jsonify(
                {"success": False, "error": t("api.projectNotFound", id=project_id)}
            ), 404

        graph_id = data.get("graph_id") or project.graph_id
        if not graph_id:
            return jsonify({"success": False, "error": t("api.graphNotBuilt")}), 400

        manager = SimulationManager()
        state = manager.create_simulation(
            project_id=project_id,
            graph_id=graph_id,
            enable_twitter=data.get("enable_twitter", True),
            enable_reddit=data.get("enable_reddit", True),
        )

        bind_simulation_to_user(
            state.simulation_id,
            project_id,
            current_user.user_id if current_user else None,
        )

        return jsonify({"success": True, "data": state.to_dict()})

    except Exception as e:
        logger.error(f"Error al crear simulación: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


def _check_simulation_prepared(simulation_id: str) -> tuple:
    """
    Verificar si la simulaciÃ³n ya estÃ¡ preparada y completada

    Condiciones de verificaciÃ³n:
    1. state.json existe y status es "ready"
    2. Archivos necesarios existen: reddit_profiles.json, twitter_profiles.csv, simulation_config.json

    Nota: Scripts de ejecuciÃ³n (run_*.py) se mantienen en directorio backend/scripts/, ya no se copian al directorio de simulaciÃ³n

    Args:
        simulation_id: ID de simulaciÃ³n

    Returns:
        (is_prepared: bool, info: dict)
    """
    import os
    from ..config import Config

    simulation_dir = os.path.join(Config.OASIS_SIMULATION_DATA_DIR, simulation_id)

    # Verificar si existe el directorio
    if not os.path.exists(simulation_dir):
        return False, {"reason": "Directorio de simulaciÃ³n no existe"}

    # Lista de archivos requeridos (no incluye scripts, scripts ubicados en backend/scripts/)
    required_files = [
        "state.json",
        "simulation_config.json",
        "reddit_profiles.json",
        "twitter_profiles.csv",
    ]

    # Verificar si existe el archivo
    existing_files = []
    missing_files = []
    for f in required_files:
        file_path = os.path.join(simulation_dir, f)
        if os.path.exists(file_path):
            existing_files.append(f)
        else:
            missing_files.append(f)

    if missing_files:
        return False, {
            "reason": "Faltan archivos necesarios",
            "missing_files": missing_files,
            "existing_files": existing_files,
        }

    # Verificar estado en state.json
    state_file = os.path.join(simulation_dir, "state.json")
    try:
        import json

        with open(state_file, "r", encoding="utf-8") as f:
            state_data = json.load(f)

        status = state_data.get("status", "")
        config_generated = state_data.get("config_generated", False)

        # Log detallado
        logger.debug(
            f"Detectando estado de preparaciÃ³n de simulaciÃ³n: {simulation_id}, status={status}, config_generated={config_generated}"
        )

        # Si config_generated=True y el archivo existe, considerar preparaciÃ³n completada
        # Los siguientes estados indican que la preparaciÃ³n estÃ¡ completada:
        # - ready: PreparaciÃ³n completada, puede ejecutarse
        # - preparing: Si config_generated=True indica completado
        # - running: En ejecuciÃ³n, preparaciÃ³n completada hace tiempo
        # - completed: EjecuciÃ³n completada, preparaciÃ³n hecha hace tiempo
        # - stopped: Detenido, preparaciÃ³n hecha hace tiempo
        # - failed: FallÃ³ la ejecuciÃ³n (pero la preparaciÃ³n estÃ¡ completa)
        prepared_statuses = [
            "ready",
            "preparing",
            "running",
            "completed",
            "stopped",
            "failed",
        ]
        if status in prepared_statuses and config_generated:
            # Obtener estadÃ­sticas de archivos
            profiles_file = os.path.join(simulation_dir, "reddit_profiles.json")
            config_file = os.path.join(simulation_dir, "simulation_config.json")

            profiles_count = 0
            if os.path.exists(profiles_file):
                with open(profiles_file, "r", encoding="utf-8") as f:
                    profiles_data = json.load(f)
                    profiles_count = (
                        len(profiles_data) if isinstance(profiles_data, list) else 0
                    )

            # Si el estado es preparing pero el archivo estÃ¡ completo, actualizar automÃ¡ticamente a ready
            if status == "preparing":
                try:
                    state_data["status"] = "ready"
                    from datetime import datetime

                    state_data["updated_at"] = datetime.now().isoformat()
                    with open(state_file, "w", encoding="utf-8") as f:
                        json.dump(state_data, f, ensure_ascii=False, indent=2)
                    logger.info(
                        f"ActualizaciÃ³n automÃ¡tica de estado de simulaciÃ³n: {simulation_id} preparing -> ready"
                    )
                    status = "ready"
                except Exception as e:
                    logger.warning(f"Error en actualizaciÃ³n automÃ¡tica de estado: {e}")

            logger.info(
                f"Resultado de detecciÃ³n de simulaciÃ³n {simulation_id}: PreparaciÃ³n completada (status={status}, config_generated={config_generated})"
            )
            return True, {
                "status": status,
                "entities_count": state_data.get("entities_count", 0),
                "profiles_count": profiles_count,
                "entity_types": state_data.get("entity_types", []),
                "config_generated": config_generated,
                "created_at": state_data.get("created_at"),
                "updated_at": state_data.get("updated_at"),
                "existing_files": existing_files,
            }
        else:
            logger.warning(
                f"Resultado de detecciÃ³n de simulaciÃ³n {simulation_id}: PreparaciÃ³n no completada (status={status}, config_generated={config_generated})"
            )
            return False, {
                "reason": f"Estado no estÃ¡ en lista de preparados o config_generated es false: status={status}, config_generated={config_generated}",
                "status": status,
                "config_generated": config_generated,
            }

    except Exception as e:
        return False, {"reason": f"Error al leer archivo de estado: {str(e)}"}


@simulation_bp.route("/prepare", methods=["POST"])
def prepare_simulation():
    """
    Preparar entorno de simulaciÃ³n (tarea asÃ­ncrona, LLM genera todos los parÃ¡metros)

    Esta es una operaciÃ³n que toma tiempo, la interfaz devolverÃ¡ inmediatamente task_id,
    usar GET /api/simulation/prepare/status para consultar el progreso

    CaracterÃ­sticas:
    - Detectar automÃ¡ticamente preparaciÃ³n completada, evitar generaciÃ³n repetida
    - Si ya estÃ¡ preparado, devolver directamente el resultado existente
    - Soportar regeneraciÃ³n forzada (force_regenerate=true)

    Pasos:
    1. Verificar si ya existe preparaciÃ³n completada
    2. Leer y filtrar entidades del grafo Zep
    3. Generar Agent Profile OASIS para cada entidad (con mecanismo de reintento)
    4. LLM genera inteligentemente configuraciÃ³n de simulaciÃ³n (con mecanismo de reintento)
    5. Guardar archivo de configuraciÃ³n y scripts preestablecidos

    Solicitud (JSON):
        {
            "simulation_id": "sim_xxxx",                   // Requerido, ID de simulaciÃ³n
            "entity_types": ["Student", "PublicFigure"],  // Opcional, especificar tipos de entidades
            "use_llm_for_profiles": true,                 // Opcional, si usar LLM para generar perfiles
            "parallel_profile_count": 5,                  // Opcional, cantidad de generaciÃ³n paralela de perfiles, por defecto 5
            "force_regenerate": false                     // Opcional, forzar regeneraciÃ³n, por defecto false
        }

    Respuesta:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "task_id": "task_xxxx",           // Devolver cuando es nueva tarea
                "status": "preparing|ready",
                "message": "Tarea de preparaciÃ³n iniciada|Ya existe preparaciÃ³n completada",
                "already_prepared": true|false    // Si ya estÃ¡ preparado completada
            }
        }
    """
    import threading
    import os
    from ..models.task import TaskManager, TaskStatus
    from ..config import Config

    try:
        data = request.get_json() or {}

        simulation_id = data.get("simulation_id")
        if not simulation_id:
            return jsonify(
                {"success": False, "error": t("api.requireSimulationId")}
            ), 400

        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)

        if not state:
            return jsonify(
                {
                    "success": False,
                    "error": t("api.simulationNotFound", id=simulation_id),
                }
            ), 404

        # Verificar si se forzarÃ¡ regeneraciÃ³n
        force_regenerate = data.get("force_regenerate", False)
        logger.info(
            f"Iniciando procesamiento de solicitud /prepare: simulation_id={simulation_id}, force_regenerate={force_regenerate}"
        )

        # Verificar si ya existe preparaciÃ³n completada (evitar generaciÃ³n repetida)
        if not force_regenerate:
            logger.debug(
                f"Verificando si simulaciÃ³n {simulation_id} ya estÃ¡ preparada completada..."
            )
            is_prepared, prepare_info = _check_simulation_prepared(simulation_id)
            logger.debug(
                f"Resultado de verificaciÃ³n: is_prepared={is_prepared}, prepare_info={prepare_info}"
            )
            if is_prepared:
                logger.info(
                    f"SimulaciÃ³n {simulation_id} ya estÃ¡ preparada completada, saltar generaciÃ³n repetida"
                )
                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "simulation_id": simulation_id,
                            "status": "ready",
                            "message": t("api.alreadyPrepared"),
                            "already_prepared": True,
                            "prepare_info": prepare_info,
                        },
                    }
                )
            else:
                logger.info(
                    f"SimulaciÃ³n {simulation_id} no estÃ¡ preparada completada, iniciarÃ¡ tarea de preparaciÃ³n"
                )

        # Obtener informaciÃ³n necesaria del proyecto
        project = ProjectManager.get_project(state.project_id)
        if not project:
            return jsonify(
                {
                    "success": False,
                    "error": t("api.projectNotFound", id=state.project_id),
                }
            ), 404

        # Obtener requisito de simulaciÃ³n
        simulation_requirement = project.simulation_requirement or ""
        if not simulation_requirement:
            return jsonify(
                {"success": False, "error": t("api.projectMissingRequirement")}
            ), 400

        # Obtener texto del documento
        document_text = ProjectManager.get_extracted_text(state.project_id) or ""

        entity_types_list = data.get("entity_types")
        use_llm_for_profiles = data.get("use_llm_for_profiles", True)
        parallel_profile_count = data.get("parallel_profile_count", 5)

        # ========== Obtener sincrÃ³nicamente cantidad de entidades (antes de iniciar tarea en segundo plano) ==========
        # AsÃ­ el frontend puede obtener inmediatamente la cantidad esperada de agentes despuÃ©s de llamar a prepare
        try:
            logger.info(
                f"Obteniendo sincrÃ³nicamente cantidad de entidades: graph_id={state.graph_id}"
            )
            backend = get_memory_backend()
            # Leer entidades rÃ¡pidamente (no requiere informaciÃ³n de bordes, solo contar cantidad)
            filtered_preview = backend.filter_defined_entities(
                graph_id=state.graph_id,
                defined_entity_types=entity_types_list,
                enrich_with_edges=False,  # No obtener informaciÃ³n de bordes, acelerar
            )
            # Guardar cantidad de entidades en estado (para que frontend obtenga inmediatamente)
            state.entities_count = filtered_preview.filtered_count
            state.entity_types = list(filtered_preview.entity_types)
            logger.info(
                f"Cantidad esperada de entidades: {filtered_preview.filtered_count}, tipos: {filtered_preview.entity_types}"
            )
        except Exception as e:
            logger.warning(
                f"Error al obtener sincrÃ³nicamente cantidad de entidades (se reintentarÃ¡ en tarea en segundo plano): {e}"
            )
            # El error no afecta el flujo posterior, la tarea en segundo plano volverÃ¡ a obtener

        # CreaciÃ³n de tarea asÃ­ncrona
        task_manager = TaskManager()
        task_id = task_manager.create_task(
            task_type="simulation_prepare",
            metadata={"simulation_id": simulation_id, "project_id": state.project_id},
        )

        # Actualizar estado de simulaciÃ³n (incluyendo cantidad de entidades obtenida previamente)
        state.status = SimulationStatus.PREPARING
        manager._save_simulation_state(state)

        # Capture locale before spawning background thread
        current_locale = get_locale()

        # Definir tarea en segundo plano
        def run_prepare():
            set_locale(current_locale)
            try:
                task_manager.update_task(
                    task_id,
                    status=TaskStatus.PROCESSING,
                    progress=0,
                    message=t("progress.startPreparingEnv"),
                )

                # Preparar simulaciÃ³n (con callback de progreso)
                # Almacenar detalles de progreso de etapa
                stage_details = {}

                def progress_callback(stage, progress, message, **kwargs):
                    # Calcular progreso total
                    stage_weights = {
                        "reading": (0, 20),  # 0-20%
                        "generating_profiles": (20, 70),  # 20-70%
                        "generating_config": (70, 90),  # 70-90%
                        "copying_scripts": (90, 100),  # 90-100%
                    }

                    start, end = stage_weights.get(stage, (0, 100))
                    current_progress = int(start + (end - start) * progress / 100)

                    # Construir informaciÃ³n de progreso detallada
                    stage_names = {
                        "reading": t("progress.readingGraphEntities"),
                        "generating_profiles": t("progress.generatingProfiles"),
                        "generating_config": t("progress.generatingSimConfig"),
                        "copying_scripts": t("progress.preparingScripts"),
                    }

                    stage_index = (
                        list(stage_weights.keys()).index(stage) + 1
                        if stage in stage_weights
                        else 1
                    )
                    total_stages = len(stage_weights)

                    # Actualizar detalles de etapa
                    stage_details[stage] = {
                        "stage_name": stage_names.get(stage, stage),
                        "stage_progress": progress,
                        "current": kwargs.get("current", 0),
                        "total": kwargs.get("total", 0),
                        "item_name": kwargs.get("item_name", ""),
                    }

                    # Construir informaciÃ³n de progreso detallada
                    detail = stage_details[stage]
                    progress_detail_data = {
                        "current_stage": stage,
                        "current_stage_name": stage_names.get(stage, stage),
                        "stage_index": stage_index,
                        "total_stages": total_stages,
                        "stage_progress": progress,
                        "current_item": detail["current"],
                        "total_items": detail["total"],
                        "item_description": message,
                    }

                    # Construir mensaje conciso
                    if detail["total"] > 0:
                        detailed_message = (
                            f"[{stage_index}/{total_stages}] {stage_names.get(stage, stage)}: "
                            f"{detail['current']}/{detail['total']} - {message}"
                        )
                    else:
                        detailed_message = f"[{stage_index}/{total_stages}] {stage_names.get(stage, stage)}: {message}"

                    task_manager.update_task(
                        task_id,
                        progress=current_progress,
                        message=detailed_message,
                        progress_detail=progress_detail_data,
                    )

                result_state = manager.prepare_simulation(
                    simulation_id=simulation_id,
                    simulation_requirement=simulation_requirement,
                    document_text=document_text,
                    defined_entity_types=entity_types_list,
                    use_llm_for_profiles=use_llm_for_profiles,
                    progress_callback=progress_callback,
                    parallel_profile_count=parallel_profile_count,
                )

                # Tarea completada
                task_manager.complete_task(
                    task_id, result=result_state.to_simple_dict()
                )

            except Exception as e:
                logger.error(f"Error al preparar simulaciÃ³n: {str(e)}")
                task_manager.fail_task(task_id, str(e))

                # Actualizar estado de simulaciÃ³n a fallido
                state = manager.get_simulation(simulation_id)
                if state:
                    state.status = SimulationStatus.FAILED
                    state.error = str(e)
                    manager._save_simulation_state(state)

        # Iniciar hilo en segundo plano
        thread = threading.Thread(target=run_prepare, daemon=True)
        thread.start()

        return jsonify(
            {
                "success": True,
                "data": {
                    "simulation_id": simulation_id,
                    "task_id": task_id,
                    "status": "preparing",
                    "message": t("api.prepareStarted"),
                    "already_prepared": False,
                    "expected_entities_count": state.entities_count,  # Cantidad esperada de agentes
                    "entity_types": state.entity_types,  # Lista de tipos de entidades
                },
            }
        )

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404

    except Exception as e:
        logger.error(f"Error al iniciar tarea de preparaciÃ³n: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/prepare/status", methods=["POST"])
def get_prepare_status():
    """
    Consultar progreso de tarea de preparaciÃ³n

    Soporta dos mÃ©todos de consulta:
    1. Consultar progreso de tarea en curso mediante task_id
    2. Verificar mediante simulation_id si ya existe preparaciÃ³n completada

    Solicitud (JSON):
        {
            "task_id": "task_xxxx",          // Opcional, task_id devuelto por prepare
            "simulation_id": "sim_xxxx"      // Opcional, ID de simulaciÃ³n (para verificar preparaciÃ³n completada)
        }

    Respuesta:
        {
            "success": true,
            "data": {
                "task_id": "task_xxxx",
                "status": "processing|completed|ready",
                "progress": 45,
                "message": "...",
                "already_prepared": true|false,  // Si ya existe preparaciÃ³n completada
                "prepare_info": {...}            // InformaciÃ³n detallada cuando ya estÃ¡ preparado completada
            }
        }
    """
    from ..models.task import TaskManager

    try:
        data = request.get_json() or {}

        task_id = data.get("task_id")
        simulation_id = data.get("simulation_id")

        # Si se proporciona simulation_id, verificar primero si ya estÃ¡ preparado completada
        if simulation_id:
            is_prepared, prepare_info = _check_simulation_prepared(simulation_id)
            if is_prepared:
                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "simulation_id": simulation_id,
                            "status": "ready",
                            "progress": 100,
                            "message": t("api.alreadyPrepared"),
                            "already_prepared": True,
                            "prepare_info": prepare_info,
                        },
                    }
                )

        # Si no hay task_id, devolver error
        if not task_id:
            if simulation_id:
                # Tiene simulation_id pero no estÃ¡ preparado completada
                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "simulation_id": simulation_id,
                            "status": "not_started",
                            "progress": 0,
                            "message": t("api.notStartedPrepare"),
                            "already_prepared": False,
                        },
                    }
                )
            return jsonify(
                {"success": False, "error": t("api.requireTaskOrSimId")}
            ), 400

        task_manager = TaskManager()
        task = task_manager.get_task(task_id)

        if not task:
            # Tarea no existe, pero si hay simulation_id, verificar si ya estÃ¡ preparado completada
            if simulation_id:
                is_prepared, prepare_info = _check_simulation_prepared(simulation_id)
                if is_prepared:
                    return jsonify(
                        {
                            "success": True,
                            "data": {
                                "simulation_id": simulation_id,
                                "task_id": task_id,
                                "status": "ready",
                                "progress": 100,
                                "message": t("api.taskCompletedPrepared"),
                                "already_prepared": True,
                                "prepare_info": prepare_info,
                            },
                        }
                    )

            return jsonify(
                {"success": False, "error": t("api.taskNotFound", id=task_id)}
            ), 404

        task_dict = task.to_dict()
        task_dict["already_prepared"] = False

        return jsonify({"success": True, "data": task_dict})

    except Exception as e:
        logger.error(f"Error al consultar estado de tarea: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@simulation_bp.route("/<simulation_id>", methods=["GET"])
def get_simulation(simulation_id: str):
    """Obtener estado de simulaciÃ³n"""
    try:
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)

        if not state:
            return jsonify(
                {
                    "success": False,
                    "error": t("api.simulationNotFound", id=simulation_id),
                }
            ), 404

        result = state.to_dict()

        # Si la simulaciÃ³n ya estÃ¡ preparada, agregar descripciÃ³n de ejecuciÃ³n
        if state.status == SimulationStatus.READY:
            result["run_instructions"] = manager.get_run_instructions(simulation_id)

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Error al obtener estado de simulaciÃ³n: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/list", methods=["GET"])
def list_simulations():
    """
    listar todas las simulaciones

    Query parámetro:
        project_id: filtrar por ID del proyecto (opcional)
    """
    try:
        current_user = get_current_user()
        project_id = request.args.get("project_id")
        limit = request.args.get("limit", 50, type=int)

        manager = SimulationManager()
        simulations = manager.list_simulations(project_id=project_id, limit=500)
        owned_ids = get_user_simulation_ids(current_user.user_id) if current_user else None
        if owned_ids is not None:
            simulations = [s for s in simulations if s.simulation_id in owned_ids]
        simulations = simulations[:limit]

        return jsonify(
            {
                "success": True,
                "data": [s.to_dict() for s in simulations],
                "count": len(simulations),
            }
        )

    except Exception as e:
        logger.error(f"Error al listar simulaciones: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


def _get_report_id_for_simulation(simulation_id: str) -> str:
    """
    Obtener el report_id mÃ¡s reciente correspondiente a simulation

    Recorrer directorio reports, encontrar report que coincida con simulation_id,
    si hay varios devolver el mÃ¡s reciente (ordenar por created_at)

    Args:
        simulation_id: ID de simulaciÃ³n

    Returns:
        report_id o None
    """
    import json
    from datetime import datetime

    # ruta del directorio reports: backend/uploads/reports
    # __file__ es app/api/simulation.py, necesito subir dos niveles a backend/
    reports_dir = os.path.join(os.path.dirname(__file__), "../../uploads/reports")
    if not os.path.exists(reports_dir):
        return None

    matching_reports = []

    try:
        for report_folder in os.listdir(reports_dir):
            report_path = os.path.join(reports_dir, report_folder)
            if not os.path.isdir(report_path):
                continue

            meta_file = os.path.join(report_path, "meta.json")
            if not os.path.exists(meta_file):
                continue

            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                if meta.get("simulation_id") == simulation_id:
                    matching_reports.append(
                        {
                            "report_id": meta.get("report_id"),
                            "created_at": meta.get("created_at", ""),
                            "status": meta.get("status", ""),
                        }
                    )
            except Exception:
                continue

        if not matching_reports:
            return None

        # Ordenar por fecha de creaciÃ³n descendente, devolver el mÃ¡s reciente
        matching_reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return matching_reports[0].get("report_id")

    except Exception as e:
        logger.warning(f"Error al buscar report de simulaciÃ³n {simulation_id}: {e}")
        return None


@simulation_bp.route("/history", methods=["GET"])
def get_simulation_history():
    """
    Obtener lista histÃ³rica de simulaciones (con detalles del proyecto)

    Usado para mostrar proyectos histÃ³ricos en pÃ¡gina de inicio, devolver lista de simulaciones con informaciÃ³n rica como nombre del proyecto, descripciÃ³n, etc.

    ParÃ¡metros Query:
        limit: LÃ­mite de cantidad a devolver (por defecto 20)

    Respuesta:
        {
            "success": true,
            "data": [
                {
                    "simulation_id": "sim_xxxx",
                    "project_id": "proj_xxxx",
                "project_name": "AnÃ¡lisis de opiniÃ³n pÃºblica de Wuhan",
                "simulation_requirement": "Si la Universidad de Wuhan publica...",
                    "status": "completed",
                    "entities_count": 68,
                    "profiles_count": 68,
                    "entity_types": ["Student", "Professor", ...],
                    "created_at": "2024-12-10",
                    "updated_at": "2024-12-10",
                    "total_rounds": 120,
                    "current_round": 120,
                    "report_id": "report_xxxx",
                    "version": "v1.0.2"
                },
                ...
            ],
            "count": 7
        }
    """
    try:
        limit = request.args.get("limit", 20, type=int)

        manager = SimulationManager()
        simulations = manager.list_simulations()[:limit]

        # Enriquecer datos de simulaciÃ³n, solo leer de archivos de Simulation
        enriched_simulations = []
        for sim in simulations:
            sim_dict = sim.to_dict()

            # Obtener informaciÃ³n de configuraciÃ³n de simulaciÃ³n (leer simulation_requirement desde simulation_config.json)
            config = manager.get_simulation_config(sim.simulation_id)
            if config:
                sim_dict["simulation_requirement"] = config.get(
                    "simulation_requirement", ""
                )
                time_config = config.get("time_config", {})
                sim_dict["total_simulation_hours"] = time_config.get(
                    "total_simulation_hours", 0
                )
                # Recomendar nÃºmero de rondas (valor de respaldo)
                recommended_rounds = int(
                    time_config.get("total_simulation_hours", 0)
                    * 60
                    / max(time_config.get("minutes_per_round", 60), 1)
                )
            else:
                sim_dict["simulation_requirement"] = ""
                sim_dict["total_simulation_hours"] = 0
                recommended_rounds = 0

            # Obtener estado de ejecuciÃ³n (leer rondas reales establecidas por usuario desde run_state.json)
            run_state = SimulationRunner.get_run_state(sim.simulation_id)
            if run_state:
                sim_dict["current_round"] = run_state.current_round
                sim_dict["runner_status"] = run_state.runner_status.value
                # Usar total_rounds establecido por usuario, si es None usar rondas recomendadas
                sim_dict["total_rounds"] = (
                    run_state.total_rounds
                    if run_state.total_rounds > 0
                    else recommended_rounds
                )
            else:
                sim_dict["current_round"] = 0
                sim_dict["runner_status"] = "idle"
                sim_dict["total_rounds"] = recommended_rounds

            # Obtener lista de archivos del proyecto relacionado (mÃ¡ximo 3 elementos)
            project = ProjectManager.get_project(sim.project_id)
            if project and hasattr(project, "files") and project.files:
                sim_dict["files"] = [
                    {"filename": f.get("filename", "Archivo desconocido")}
                    for f in project.files[:3]
                ]
            else:
                sim_dict["files"] = []

            # Obtener report_id relacionado (buscar el report mÃ¡s reciente de esta simulaciÃ³n)
            sim_dict["report_id"] = _get_report_id_for_simulation(sim.simulation_id)

            # Agregar nÃºmero de versiÃ³n
            sim_dict["version"] = "v1.0.2"

            # Formatear fecha
            try:
                created_date = sim_dict.get("created_at", "")[:10]
                sim_dict["created_date"] = created_date
            except:
                sim_dict["created_date"] = ""

            enriched_simulations.append(sim_dict)

        return jsonify(
            {
                "success": True,
                "data": enriched_simulations,
                "count": len(enriched_simulations),
            }
        )

    except Exception as e:
        logger.error(f"Error al obtener historial de simulaciones: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/profiles", methods=["GET"])
def get_simulation_profiles(simulation_id: str):
    """
    Obtener Agent Profile de la simulaciÃ³n

    ParÃ¡metros Query:
        platform: Tipo de plataforma (reddit/twitter, por defecto reddit)
    """
    try:
        platform = request.args.get("platform", "reddit")

        manager = SimulationManager()
        profiles = manager.get_profiles(simulation_id, platform=platform)

        return jsonify(
            {
                "success": True,
                "data": {
                    "platform": platform,
                    "count": len(profiles),
                    "profiles": profiles,
                },
            }
        )

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404

    except Exception as e:
        logger.error(f"Error al obtener perfil: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/profiles/realtime", methods=["GET"])
def get_simulation_profiles_realtime(simulation_id: str):
    """
    Obtener Agent Profile de simulaciÃ³n en tiempo real (usado para ver progreso durante generaciÃ³n)

    Diferencias con el endpoint /profiles:
    - Leer archivos directamente, sin pasar por SimulationManager
    - Apto para ver en tiempo real durante generaciÃ³n
    - Devolver metadatos adicionales (como tiempo de modificaciÃ³n de archivo, si estÃ¡ generando, etc.)

    ParÃ¡metros Query:
        platform: Tipo de plataforma (reddit/twitter, por defecto reddit)

    Volverï¼š
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "platform": "reddit",
                "count": 15,
                "total_expected": 93,  // NÃºmero total esperado (si hay)
                "is_generating": true,  // si estÃ¡ generando
                "file_exists": true,
                "file_modified_at": "2025-12-04T18:20:00",
                "profiles": [...]
            }
        }
    """
    import json
    import csv
    from datetime import datetime

    try:
        platform = request.args.get("platform", "reddit")

        # ObtenersimulaciÃ³ndirectorio
        sim_dir = os.path.join(Config.OASIS_SIMULATION_DATA_DIR, simulation_id)

        if not os.path.exists(sim_dir):
            return jsonify(
                {
                    "success": False,
                    "error": t("api.simulationNotFound", id=simulation_id),
                }
            ), 404

        # Determinar ruta de archivo
        if platform == "reddit":
            profiles_file = os.path.join(sim_dir, "reddit_profiles.json")
        else:
            profiles_file = os.path.join(sim_dir, "twitter_profiles.csv")

        # Verificar si existe el archivo
        file_exists = os.path.exists(profiles_file)
        profiles = []
        file_modified_at = None

        if file_exists:
            # Obtener tiempo de modificaciÃ³n del archivo
            file_stat = os.stat(profiles_file)
            file_modified_at = datetime.fromtimestamp(file_stat.st_mtime).isoformat()

            try:
                if platform == "reddit":
                    with open(profiles_file, "r", encoding="utf-8") as f:
                        profiles = json.load(f)
                else:
                    with open(profiles_file, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        profiles = list(reader)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(
                    f"Error al leer archivo profiles (puede estar escribiendo): {e}"
                )
                profiles = []

        # Verificar si estÃ¡ generando (mediante state.json)
        is_generating = False
        total_expected = None

        state_file = os.path.join(sim_dir, "state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    status = state_data.get("status", "")
                    is_generating = status == "preparing"
                    total_expected = state_data.get("entities_count")
            except Exception:
                pass

        return jsonify(
            {
                "success": True,
                "data": {
                    "simulation_id": simulation_id,
                    "platform": platform,
                    "count": len(profiles),
                    "total_expected": total_expected,
                    "is_generating": is_generating,
                    "file_exists": file_exists,
                    "file_modified_at": file_modified_at,
                    "profiles": profiles,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error al obtener perfil en tiempo real: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/config/realtime", methods=["GET"])
def get_simulation_config_realtime(simulation_id: str):
    """
    Obtener configuraciÃ³n de simulaciÃ³n en tiempo real (usado para ver progreso durante generaciÃ³n)

    Diferencias con el endpoint /config:
    - Leer archivos directamente, sin pasar por SimulationManager
    - Apto para ver en tiempo real durante generaciÃ³n
    - Devolver metadatos adicionales (como tiempo de modificaciÃ³n de archivo, si estÃ¡ generando, etc.)
    - Puede devolver informaciÃ³n parcial incluso si la configuraciÃ³n no estÃ¡ completamente generada

    Respuesta:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "file_exists": true,
                "file_modified_at": "2025-12-04T18:20:00",
                "is_generating": true,  // Si estÃ¡ generando
                "generation_stage": "generating_config",  // Etapa actual de generaciÃ³n
                "config": {...}  // Contenido de configuraciÃ³n (si existe)
            }
        }
    """
    import json
    from datetime import datetime

    try:
        # Obtener directorio de simulaciÃ³n
        sim_dir = os.path.join(Config.OASIS_SIMULATION_DATA_DIR, simulation_id)

        if not os.path.exists(sim_dir):
            return jsonify(
                {
                    "success": False,
                    "error": t("api.simulationNotFound", id=simulation_id),
                }
            ), 404

        # Ruta de archivo de configuraciÃ³n
        config_file = os.path.join(sim_dir, "simulation_config.json")

        # Verificar si existe el archivo
        file_exists = os.path.exists(config_file)
        config = None
        file_modified_at = None

        if file_exists:
            # Obtener tiempo de modificaciÃ³n del archivo
            file_stat = os.stat(config_file)
            file_modified_at = datetime.fromtimestamp(file_stat.st_mtime).isoformat()

            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(
                    f"leer archivo config fallido (posiblemente escribiendo): {e}"
                )
                config = None

        # Verificar si estÃ¡ en generaciÃ³n (mediante state.json)
        is_generating = False
        generation_stage = None
        config_generated = False

        state_file = os.path.join(sim_dir, "state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    status = state_data.get("status", "")
                    is_generating = status == "preparing"
                    config_generated = state_data.get("config_generated", False)

                    # Determinar etapa actual
                    if is_generating:
                        if state_data.get("profiles_generated", False):
                            generation_stage = "generating_config"
                        else:
                            generation_stage = "generating_profiles"
                    elif status == "ready":
                        generation_stage = "completed"
            except Exception:
                pass

        # Construir datos de retorno
        response_data = {
            "simulation_id": simulation_id,
            "file_exists": file_exists,
            "file_modified_at": file_modified_at,
            "is_generating": is_generating,
            "generation_stage": generation_stage,
            "config_generated": config_generated,
            "config": config,
        }

        # Si la configuraciÃ³n existe, extraer informaciÃ³n de estadÃ­sticas clave
        if config:
            response_data["summary"] = {
                "total_agents": len(config.get("agent_configs", [])),
                "simulation_hours": config.get("time_config", {}).get(
                    "total_simulation_hours"
                ),
                "initial_posts_count": len(
                    config.get("event_config", {}).get("initial_posts", [])
                ),
                "hot_topics_count": len(
                    config.get("event_config", {}).get("hot_topics", [])
                ),
                "has_twitter_config": "twitter_config" in config,
                "has_reddit_config": "reddit_config" in config,
                "generated_at": config.get("generated_at"),
                "llm_model": config.get("llm_model"),
            }

        return jsonify({"success": True, "data": response_data})

    except Exception as e:
        logger.error(f"Error al obtener configuraciÃ³n en tiempo real: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/config", methods=["GET"])
def get_simulation_config(simulation_id: str):
    """
    Obtener configuraciÃ³n de simulaciÃ³n (LLM genera inteligentemente la configuraciÃ³n completa)

    Volver incluye:
        - time_config: ConfiguraciÃ³n de tiempo (duraciÃ³n de simulaciÃ³n, nÃºmero de rondas, pico/horas pico)
        - agent_configs: cada elemento de Agent: configuraciÃ³n de actividad (nivel de actividad, frecuencia de publicaciones, posiciÃ³n, etc.)
        - event_config: ConfiguraciÃ³n de eventos (publicaciones iniciales, temas candentes)
        - platform_configs: configuraciÃ³n de plataforma
        - generation_reasoning: descripciÃ³n del razonamiento de configuraciÃ³n de LLM
    """
    try:
        manager = SimulationManager()
        config = manager.get_simulation_config(simulation_id)

        if not config:
            return jsonify({"success": False, "error": t("api.configNotFound")}), 404

        return jsonify({"success": True, "data": config})

    except Exception as e:
        logger.error(f"Error al obtener configuraciÃ³n: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/config/download", methods=["GET"])
def download_simulation_config(simulation_id: str):
    """descargarsimulaciÃ³nconfiguraciÃ³narchivo"""
    try:
        manager = SimulationManager()
        sim_dir = manager._get_simulation_dir(simulation_id)
        config_path = os.path.join(sim_dir, "simulation_config.json")

        if not os.path.exists(config_path):
            return jsonify(
                {"success": False, "error": t("api.configFileNotFound")}
            ), 404

        return send_file(
            config_path, as_attachment=True, download_name="simulation_config.json"
        )

    except Exception as e:
        logger.error(f"Error al descargar configuraciÃ³n: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/script/<script_name>/download", methods=["GET"])
def download_simulation_script(script_name: str):
    """
    descargar script de ejecuciÃ³n de simulaciÃ³n (script general, ubicado en backend/scripts/)

    script_name (valores opcionales):
        - run_twitter_simulation.py
        - run_reddit_simulation.py
        - run_parallel_simulation.py
        - action_logger.py
    """
    try:
        # scriptubicado en backend/scripts/ directorio
        scripts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../scripts")
        )

        # Verificar nombre del script
        allowed_scripts = [
            "run_twitter_simulation.py",
            "run_reddit_simulation.py",
            "run_parallel_simulation.py",
            "action_logger.py",
        ]

        if script_name not in allowed_scripts:
            return jsonify(
                {
                    "success": False,
                    "error": t(
                        "api.unknownScript", name=script_name, allowed=allowed_scripts
                    ),
                }
            ), 400

        script_path = os.path.join(scripts_dir, script_name)

        if not os.path.exists(script_path):
            return jsonify(
                {
                    "success": False,
                    "error": t("api.scriptFileNotFound", name=script_name),
                }
            ), 404

        return send_file(script_path, as_attachment=True, download_name=script_name)

    except Exception as e:
        logger.error(f"Error al descargar script: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


# ============== Interfaz de generaciÃ³n de perfiles (uso independiente) ==============


@simulation_bp.route("/generate-profiles", methods=["POST"])
def generate_profiles():
    """
    Generar OASIS Agent Profile directamente desde Grafo (no crear simulaciÃ³n)

    solicitud (JSON):
        {
            "graph_id": "mirofish_xxxx",     // Requerido
            "entity_types": ["Student"],      // Opcional
            "use_llm": true,                  // Opcional
            "platform": "reddit"              // Opcional
        }
    """
    try:
        data = request.get_json() or {}

        graph_id = data.get("graph_id")
        if not graph_id:
            return jsonify({"success": False, "error": t("api.requireGraphId")}), 400

        entity_types = data.get("entity_types")
        use_llm = data.get("use_llm", True)
        platform = data.get("platform", "reddit")

        reader = ZepEntityReader()
        filtered = reader.filter_defined_entities(
            graph_id=graph_id, defined_entity_types=entity_types, enrich_with_edges=True
        )

        if filtered.filtered_count == 0:
            return jsonify(
                {"success": False, "error": t("api.noMatchingEntities")}
            ), 400

        generator = OasisProfileGenerator()
        profiles = generator.generate_profiles_from_entities(
            entities=filtered.entities, use_llm=use_llm
        )

        if platform == "reddit":
            profiles_data = [p.to_reddit_format() for p in profiles]
        elif platform == "twitter":
            profiles_data = [p.to_twitter_format() for p in profiles]
        else:
            profiles_data = [p.to_dict() for p in profiles]

        return jsonify(
            {
                "success": True,
                "data": {
                    "platform": platform,
                    "entity_types": list(filtered.entity_types),
                    "count": len(profiles_data),
                    "profiles": profiles_data,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error al generar perfil: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


# ============== Interfaz de control de ejecuciÃ³n de simulaciÃ³n ==============


@simulation_bp.route("/start", methods=["POST"])
def start_simulation():
    """
    Iniciar ejecuciÃ³n de simulaciÃ³n

    Solicitud (JSON):
        {
            "simulation_id": "sim_xxxx",          // Requerido, ID de simulaciÃ³n
            "platform": "parallel",                // Opcional: twitter / reddit / parallel (por defecto)
            "max_rounds": 100,                     // Opcional: nÃºmero mÃ¡ximo de rondas de simulaciÃ³n, para truncar simulaciones largas
            "enable_graph_memory_update": false,   // Opcional: si actualizar actividades de Agent a memoria del Grafo Zep dinÃ¡micamente
            "force": false                         // Opcional: forzar reinicio (detendrÃ¡ simulaciÃ³n en ejecuciÃ³n y limpiarÃ¡ logs)
        }

    Sobre parÃ¡metro force:
        - Al habilitar, si la simulaciÃ³n estÃ¡ ejecutÃ¡ndose o completada, detendrÃ¡ primero y limpiarÃ¡ logs de ejecuciÃ³n
        - El contenido a limpiar incluye: run_state.json, actions.jsonl, simulation.log, etc.
        - No limpiarÃ¡ archivos de configuraciÃ³n (simulation_config.json) y archivos de perfil
        - Apto para escenarios donde necesita re-ejecutar simulaciÃ³n

    Sobre enable_graph_memory_update:
        - Al habilitar, todas las actividades de Agent en simulaciÃ³n (publicar, comentar, me gusta, etc.) se actualizarÃ¡n en tiempo real al Grafo Zep
        - Esto permite que el Grafo "recuerde" el proceso de simulaciÃ³n, para anÃ¡lisis posterior o conversaciÃ³n con AI
        - Requiere que el proyecto relacionado con la simulaciÃ³n tenga un graph_id vÃ¡lido
        - Adopta mecanismo de actualizaciÃ³n por lotes, reducir nÃºmero de llamadas API

    Respuesta:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "runner_status": "running",
                "process_pid": 12345,
                "twitter_running": true,
                "reddit_running": true,
                "started_at": "2025-12-01T10:00:00",
                "graph_memory_update_enabled": true,  // Si habilitÃ³ actualizaciÃ³n de memoria del Grafo
                "force_restarted": true               // Si es reinicio forzado
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get("simulation_id")
        if not simulation_id:
            return jsonify(
                {"success": False, "error": t("api.requireSimulationId")}
            ), 400

        platform = data.get("platform", "parallel")
        max_rounds = data.get(
            "max_rounds"
        )  # Opcional: nÃºmero mÃ¡ximo de rondas de simulaciÃ³n
        enable_graph_memory_update = data.get(
            "enable_graph_memory_update", False
        )  # Opcional: si habilitar actualizaciÃ³n de memoria del Grafo
        force = data.get("force", False)  # Opcional: forzar reiniciar

        # VerificaciÃ³n max_rounds parÃ¡metro
        if max_rounds is not None:
            try:
                max_rounds = int(max_rounds)
                if max_rounds <= 0:
                    return jsonify(
                        {"success": False, "error": t("api.maxRoundsPositive")}
                    ), 400
            except (ValueError, TypeError):
                return jsonify(
                    {"success": False, "error": t("api.maxRoundsInvalid")}
                ), 400

        if platform not in ["twitter", "reddit", "parallel"]:
            return jsonify(
                {"success": False, "error": t("api.invalidPlatform", platform=platform)}
            ), 400

        # Verificar si simulaciÃ³n ya estÃ¡ preparada
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)

        if not state:
            return jsonify(
                {
                    "success": False,
                    "error": t("api.simulationNotFound", id=simulation_id),
                }
            ), 404

        force_restarted = False

        # Procesamiento inteligente del estado: Si preparaciÃ³n completada, permitir reiniciar
        if state.status != SimulationStatus.READY:
            # Verificar si preparaciÃ³n completada
            is_prepared, prepare_info = _check_simulation_prepared(simulation_id)

            if is_prepared:
                # preparaciÃ³n completada, verificar si hay proceso ejecutÃ¡ndose
                if state.status == SimulationStatus.RUNNING:
                    # Verificar si proceso de simulaciÃ³n realmente estÃ¡ ejecutÃ¡ndose
                    run_state = SimulationRunner.get_run_state(simulation_id)
                    if run_state and run_state.runner_status.value == "running":
                        # Proceso realmente estÃ¡ ejecutÃ¡ndose
                        if force:
                            # forzar modo: detener simulaciÃ³n que se estÃ¡ ejecutando
                            logger.info(
                                f"forzar modo: detener simulaciÃ³n que se estÃ¡ ejecutando {simulation_id}"
                            )
                            try:
                                SimulationRunner.stop_simulation(simulation_id)
                            except Exception as e:
                                logger.warning(
                                    f"detener simulaciÃ³n apareciÃ³ advertencia: {str(e)}"
                                )
                        else:
                            return jsonify(
                                {
                                    "success": False,
                                    "error": t("api.simRunningForceHint"),
                                }
                            ), 400

                # Si es forzar modo, limpiar log de ejecuciÃ³n
                if force:
                    logger.info(
                        f"Modo forzado: limpiar log de simulaciÃ³n {simulation_id}"
                    )
                    cleanup_result = SimulationRunner.cleanup_simulation_logs(
                        simulation_id
                    )
                    if not cleanup_result.get("success"):
                        logger.warning(
                            f"limpiar log apareciÃ³ advertencia: {cleanup_result.get('errors')}"
                        )
                    force_restarted = True

                # Proceso no existe o ya terminado, reiniciar estado a ready
                logger.info(
                    f"simulaciÃ³n {simulation_id} preparaciÃ³n completada, reiniciar estado a ready (estado original: {state.status.value})"
                )
                state.status = SimulationStatus.READY
                manager._save_simulation_state(state)
            else:
                # preparaciÃ³n no completada
                return jsonify(
                    {
                        "success": False,
                        "error": t("api.simNotReady", status=state.status.value),
                    }
                ), 400

        # Obtener ID de Grafo (usado para actualizaciÃ³n de memoria del Grafo)
        graph_id = None
        if enable_graph_memory_update:
            # Validar que MEMORY_BACKEND sea "zep" para esta funcionalidad
            if Config.MEMORY_BACKEND != "zep":
                return jsonify(
                    {
                        "success": False,
                        "error": t(
                            "api.memoryBackendNotSupported",
                            backend=Config.MEMORY_BACKEND,
                        ),
                    }
                ), 400

            # Obtener graph_id desde estado de simulaciÃ³n o proyecto
            graph_id = state.graph_id
            if not graph_id:
                # Intentar obtener desde proyecto
                project = ProjectManager.get_project(state.project_id)
                if project:
                    graph_id = project.graph_id

            if not graph_id:
                return jsonify(
                    {"success": False, "error": t("api.graphIdRequiredForMemory")}
                ), 400

            logger.info(
                f"habilitar actualizaciÃ³n de memoria del Grafo: simulation_id={simulation_id}, graph_id={graph_id}"
            )

        # iniciar simulaciÃ³n
        run_state = SimulationRunner.start_simulation(
            simulation_id=simulation_id,
            platform=platform,
            max_rounds=max_rounds,
            enable_graph_memory_update=enable_graph_memory_update,
            graph_id=graph_id,
        )

        # Actualizar estado de simulaciÃ³n
        state.status = SimulationStatus.RUNNING
        manager._save_simulation_state(state)

        response_data = run_state.to_dict()
        if max_rounds:
            response_data["max_rounds_applied"] = max_rounds
        response_data["graph_memory_update_enabled"] = enable_graph_memory_update
        response_data["force_restarted"] = force_restarted
        if enable_graph_memory_update:
            response_data["graph_id"] = graph_id

        return jsonify({"success": True, "data": response_data})

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        logger.error(f"iniciar simulaciÃ³n fallida: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/stop", methods=["POST"])
def stop_simulation():
    """
    detener simulaciÃ³n

    solicitud (JSON):
        {
            "simulation_id": "sim_xxxx"  // Requerido, ID de simulaciÃ³n
        }

    Volver:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "runner_status": "stopped",
                "completed_at": "2025-12-01T12:00:00"
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get("simulation_id")
        if not simulation_id:
            return jsonify(
                {"success": False, "error": t("api.requireSimulationId")}
            ), 400

        run_state = SimulationRunner.stop_simulation(simulation_id)

        # Actualizar estado de simulaciÃ³n
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        if state:
            state.status = SimulationStatus.PAUSED
            manager._save_simulation_state(state)

        return jsonify({"success": True, "data": run_state.to_dict()})

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        logger.error(f"detener simulaciÃ³n fallida: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


# ============== interfaz de monitoreo de estado en tiempo real ==============


@simulation_bp.route("/<simulation_id>/run-status", methods=["GET"])
def get_run_status(simulation_id: str):
    """
    Obtener estado de ejecuciÃ³n en tiempo real de simulaciÃ³n (usado para consulta de rondas del frontend)

    Volver:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "runner_status": "running",
                "current_round": 5,
                "total_rounds": 144,
                "progress_percent": 3.5,
                "simulated_hours": 2,
                "total_simulation_hours": 72,
                "twitter_running": true,
                "reddit_running": true,
                "twitter_actions_count": 150,
                "reddit_actions_count": 200,
                "total_actions_count": 350,
                "started_at": "2025-12-01T10:00:00",
                "updated_at": "2025-12-01T10:30:00"
            }
        }
    """
    try:
        run_state = SimulationRunner.get_run_state(simulation_id)

        if not run_state:
            return jsonify(
                {
                    "success": True,
                    "data": {
                        "simulation_id": simulation_id,
                        "runner_status": "idle",
                        "current_round": 0,
                        "total_rounds": 0,
                        "progress_percent": 0,
                        "twitter_actions_count": 0,
                        "reddit_actions_count": 0,
                        "total_actions_count": 0,
                    },
                }
            )

        return jsonify({"success": True, "data": run_state.to_dict()})

    except Exception as e:
        logger.error(f"Obtener estado de ejecuciÃ³n fallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/run-status/detail", methods=["GET"])
def get_run_status_detail(simulation_id: str):
    """
    Obtener estado detallado de ejecuciÃ³n de simulaciÃ³n (incluye todas las acciones)

    usado para presentaciÃ³n dinÃ¡mica en tiempo real del frontend

    Query parÃ¡metro:
        platform: filtrar plataforma (twitter/reddit, opcional)

    Volver:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "runner_status": "running",
                "current_round": 5,
                ...
                "all_actions": [
                    {
                        "round_num": 5,
                        "timestamp": "2025-12-01T10:30:00",
                        "platform": "twitter",
                        "agent_id": 3,
                        "agent_name": "Agent Name",
                        "action_type": "CREATE_POST",
                        "action_args": {"content": "..."},
                        "result": null,
                        "success": true
                    },
                    ...
                ],
                "twitter_actions": [...],  # todas las acciones de plataforma Twitter
                "reddit_actions": [...]    # todas las acciones de plataforma Reddit
            }
        }
    """
    try:
        run_state = SimulationRunner.get_run_state(simulation_id)
        platform_filter = request.args.get("platform")

        if not run_state:
            return jsonify(
                {
                    "success": True,
                    "data": {
                        "simulation_id": simulation_id,
                        "runner_status": "idle",
                        "all_actions": [],
                        "twitter_actions": [],
                        "reddit_actions": [],
                    },
                }
            )

        # Obtener lista completa de acciones
        all_actions = SimulationRunner.get_all_actions(
            simulation_id=simulation_id, platform=platform_filter
        )

        # Obtener acciones por plataforma
        twitter_actions = (
            SimulationRunner.get_all_actions(
                simulation_id=simulation_id, platform="twitter"
            )
            if not platform_filter or platform_filter == "twitter"
            else []
        )

        reddit_actions = (
            SimulationRunner.get_all_actions(
                simulation_id=simulation_id, platform="reddit"
            )
            if not platform_filter or platform_filter == "reddit"
            else []
        )

        # Obtener acciones de ronda actual (recent_actions solo muestra la Ãºltima ronda)
        current_round = run_state.current_round
        recent_actions = (
            SimulationRunner.get_all_actions(
                simulation_id=simulation_id,
                platform=platform_filter,
                round_num=current_round,
            )
            if current_round > 0
            else []
        )

        # Obtener informaciÃ³n bÃ¡sica
        result = run_state.to_dict()
        result["all_actions"] = [a.to_dict() for a in all_actions]
        result["twitter_actions"] = [a.to_dict() for a in twitter_actions]
        result["reddit_actions"] = [a.to_dict() for a in reddit_actions]
        result["rounds_count"] = len(run_state.rounds)
        # recent_actions solo muestra contenido de dos plataformas de la Ãºltima ronda
        result["recent_actions"] = [a.to_dict() for a in recent_actions]

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Obtener estado detallado fallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/actions", methods=["GET"])
def get_simulation_actions(simulation_id: str):
    """
    Obtener historial de acciones de Agent en simulaciÃ³n

    Query parÃ¡metro:
        limit: Cantidad a devolver (por defecto 100)
        offset: Desplazamiento (por defecto 0)
        platform: filtrar plataforma (twitter/reddit)
        agent_id: filtrar ID de Agent
        round_num: filtrar nÃºmero de rondas

    Volver:
        {
            "success": true,
            "data": {
                "count": 100,
                "actions": [...]
            }
        }
    """
    try:
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        platform = request.args.get("platform")
        agent_id = request.args.get("agent_id", type=int)
        round_num = request.args.get("round_num", type=int)

        actions = SimulationRunner.get_actions(
            simulation_id=simulation_id,
            limit=limit,
            offset=offset,
            platform=platform,
            agent_id=agent_id,
            round_num=round_num,
        )

        return jsonify(
            {
                "success": True,
                "data": {
                    "count": len(actions),
                    "actions": [a.to_dict() for a in actions],
                },
            }
        )

    except Exception as e:
        logger.error(f"Obtener historial de acciones fallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/timeline", methods=["GET"])
def get_simulation_timeline(simulation_id: str):
    """
    Obtener lÃ­nea de tiempo de simulaciÃ³n (resumido por nÃºmero de rondas)

    usado para presentar barra de progreso y vista de lÃ­nea de tiempo en frontend

    Query parÃ¡metro:
        start_round: ronda inicial (por defecto 0)
        end_round: ronda final (por defecto todas)

    Volver informaciÃ³n resumida de cada ronda
    """
    try:
        start_round = request.args.get("start_round", 0, type=int)
        end_round = request.args.get("end_round", type=int)

        timeline = SimulationRunner.get_timeline(
            simulation_id=simulation_id, start_round=start_round, end_round=end_round
        )

        return jsonify(
            {
                "success": True,
                "data": {"rounds_count": len(timeline), "timeline": timeline},
            }
        )

    except Exception as e:
        logger.error(f"Obtener lÃ­nea de tiempoFallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/agent-stats", methods=["GET"])
def get_agent_stats(simulation_id: str):
    """
    Obtener informaciÃ³n de estadÃ­sticas de cada elemento de Agent

    usado para presentaciÃ³n de nivel de actividad de Agent y distribuciÃ³n de acciones en frontend
    """
    try:
        stats = SimulationRunner.get_agent_stats(simulation_id)

        return jsonify(
            {"success": True, "data": {"agents_count": len(stats), "stats": stats}}
        )

    except Exception as e:
        logger.error(f"Obtener AgentestadÃ­sticasFallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


# ============== interfaz de consulta de base de datos ==============


@simulation_bp.route("/<simulation_id>/posts", methods=["GET"])
def get_simulation_posts(simulation_id: str):
    """
    Obtener publicaciones en simulaciÃ³n

    Query parÃ¡metro:
        platform: tipo de plataforma (twitter/reddit)
        limit: Cantidad a devolver (por defecto 50)
        offset: Desplazamiento

    Volver lista de publicaciones (leer desde base de datos SQLite)
    """
    try:
        platform = request.args.get("platform", "reddit")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        sim_dir = os.path.join(
            os.path.dirname(__file__), f"../../uploads/simulations/{simulation_id}"
        )

        db_file = f"{platform}_simulation.db"
        db_path = os.path.join(sim_dir, db_file)

        if not os.path.exists(db_path):
            return jsonify(
                {
                    "success": True,
                    "data": {
                        "platform": platform,
                        "count": 0,
                        "posts": [],
                        "message": t("api.dbNotExist"),
                    },
                }
            )

        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM post 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )

            posts = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT COUNT(*) FROM post")
            total = cursor.fetchone()[0]

        except sqlite3.OperationalError:
            posts = []
            total = 0

        conn.close()

        return jsonify(
            {
                "success": True,
                "data": {
                    "platform": platform,
                    "total": total,
                    "count": len(posts),
                    "posts": posts,
                },
            }
        )

    except Exception as e:
        logger.error(f"Obtener publicacionesFallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/<simulation_id>/comments", methods=["GET"])
def get_simulation_comments(simulation_id: str):
    """
    Obtener comentarios en simulaciÃ³n (solo Reddit)

    Query parÃ¡metro:
        post_id: filtrar ID de publicaciÃ³n (opcional)
        limit: Cantidad a devolver
        offset: Desplazamiento
    """
    try:
        post_id = request.args.get("post_id")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        sim_dir = os.path.join(
            os.path.dirname(__file__), f"../../uploads/simulations/{simulation_id}"
        )

        db_path = os.path.join(sim_dir, "reddit_simulation.db")

        if not os.path.exists(db_path):
            return jsonify({"success": True, "data": {"count": 0, "comments": []}})

        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            if post_id:
                cursor.execute(
                    """
                    SELECT * FROM comment 
                    WHERE post_id = ?
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """,
                    (post_id, limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM comment 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

            comments = [dict(row) for row in cursor.fetchall()]

        except sqlite3.OperationalError:
            comments = []

        conn.close()

        return jsonify(
            {"success": True, "data": {"count": len(comments), "comments": comments}}
        )

    except Exception as e:
        logger.error(f"Obtener comentariosFallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


# ============== interfaz de entrevista Interview ==============


@simulation_bp.route("/interview", methods=["POST"])
def interview_agent():
    """
    Entrevistar elemento individual de Agent

    Nota: esta/este funciÃ³n necesita que el entorno de simulaciÃ³n estÃ© en estado ejecutÃ¡ndose (entrar en modo Pendiente despuÃ©s de completar ciclo de simulaciÃ³n)

    solicitud (JSON):
        {
            "simulation_id": "sim_xxxx",       // Requerido, ID de simulaciÃ³n
            "agent_id": 0,                     // Requerido, ID de Agent
            "prompt": "Â¿CuÃ¡l es tu opiniÃ³n sobre este asunto?",  // Requerido, pregunta de entrevista
            "platform": "twitter",             // Opcional, especificar plataforma (twitter/reddit)
                                                // Si no se especifica: simular entrevista de dos plataformas simultÃ¡neamente
            "timeout": 60                      // Opcional, tiempo de espera (segundos), por defecto 60
        }

    Volver (si no se especifica plataforma, modo de dos plataformas):
        {
            "success": true,
            "data": {
                "agent_id": 0,
                "prompt": "Â¿CuÃ¡l es tu opiniÃ³n sobre este asunto?",
                "result": {
                    "agent_id": 0,
                    "prompt": "...",
                    "platforms": {
                        "twitter": {"agent_id": 0, "response": "...", "platform": "twitter"},
                        "reddit": {"agent_id": 0, "response": "...", "platform": "reddit"}
                    }
                },
                "timestamp": "2025-12-08T10:00:01"
            }
        }

    Volver (si se especifica plataforma):
        {
            "success": true,
            "data": {
                "agent_id": 0,
                "prompt": "Â¿CuÃ¡l es tu opiniÃ³n sobre este asunto?",
                "result": {
                    "agent_id": 0,
                    "response": "Creo que...",
                    "platform": "twitter",
                    "timestamp": "2025-12-08T10:00:00"
                },
                "timestamp": "2025-12-08T10:00:01"
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get("simulation_id")
        platform = data.get(
            "platform"
        )  # Si no se especifica, volver historial de dos plataformas
        agent_id = data.get("agent_id")
        limit = data.get("limit", 100)

        if not simulation_id:
            return jsonify(
                {"success": False, "error": t("api.requireSimulationId")}
            ), 400

        history = SimulationRunner.get_interview_history(
            simulation_id=simulation_id,
            platform=platform,
            agent_id=agent_id,
            limit=limit,
        )

        return jsonify(
            {"success": True, "data": {"count": len(history), "history": history}}
        )

    except Exception as e:
        logger.error(f"ObtenerInterviewhistorialFallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/env-status", methods=["POST"])
def get_env_status():
    """
    Obtener estado de entorno de simulaciÃ³n

    Verificar si entorno de simulaciÃ³n estÃ¡ vivo (puede recibir comando de entrevista)

    solicitud (JSON):
        {
            "simulation_id": "sim_xxxx"  // Requerido, ID de simulaciÃ³n
        }

    Volver:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "env_alive": true,
                "twitter_available": true,
                "reddit_available": true,
                "message": "Entorno estÃ¡ ejecutÃ¡ndose y listo para comandos de entrevista"
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get("simulation_id")

        if not simulation_id:
            return jsonify(
                {"success": False, "error": t("api.requireSimulationId")}
            ), 400

        env_alive = SimulationRunner.check_env_alive(simulation_id)

        # Obtener informaciÃ³n de estado mÃ¡s detallada
        env_status = SimulationRunner.get_env_status_detail(simulation_id)

        if env_alive:
            message = t("api.envRunning")
        else:
            message = t("api.envNotRunningShort")

        return jsonify(
            {
                "success": True,
                "data": {
                    "simulation_id": simulation_id,
                    "env_alive": env_alive,
                    "twitter_available": env_status.get("twitter_available", False),
                    "reddit_available": env_status.get("reddit_available", False),
                    "message": message,
                },
            }
        )

    except Exception as e:
        logger.error(f"Obtener estado de entornoFallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500


@simulation_bp.route("/close-env", methods=["POST"])
def close_simulation_env():
    """
    Cerrar entorno de simulaciÃ³n

    Enviar comando de cerrar entorno a simulaciÃ³n, hacer que salga de modo Pendiente elegantemente.

    Nota: esto es diferente de interfaz /stop, /stop forzarÃ¡ terminar proceso,
    mientras esta interfaz harÃ¡ que simulaciÃ³n salga del entorno elegantemente.

    solicitud (JSON):
        {
            "simulation_id": "sim_xxxx",  // Requerido, ID de simulaciÃ³n
            "timeout": 30                  // Opcional, tiempo de espera (segundos), por defecto 30
        }

    Volver:
        {
            "success": true,
            "data": {
                "message": "comando de cerrar entorno ya enviado",
                "result": {...},
                "timestamp": "2025-12-08T10:00:01"
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get("simulation_id")
        timeout = data.get("timeout", 30)

        if not simulation_id:
            return jsonify(
                {"success": False, "error": t("api.requireSimulationId")}
            ), 400

        result = SimulationRunner.close_simulation_env(
            simulation_id=simulation_id, timeout=timeout
        )

        # Actualizar estado de simulaciÃ³n
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        if state:
            state.status = SimulationStatus.COMPLETED
            manager._save_simulation_state(state)

        return jsonify({"success": result.get("success", False), "data": result})

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        logger.error(f"Cerrar entorno fallido: {str(e)}")
        return jsonify(
            {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        ), 500






