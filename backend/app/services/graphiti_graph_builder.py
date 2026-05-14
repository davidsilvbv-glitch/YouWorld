"""
Graphiti Graph Builder Service
Implementación de construcción de grafos para Graphiti + Neo4j

Replica la interfaz de GraphBuilderService para que el API endpoint
funcione indistintamente con Zep Cloud o Graphiti según MEMORY_BACKEND.
"""

import uuid
import re
from typing import Dict, Any, List, Optional, Callable

from ..memory.factory import get_memory_backend
from ..memory.base import GraphInfo
from ..models.project import ProjectManager
from ..services.text_processor import TextProcessor
from ..services.graph_serializers import build_graph_data_response
from ..utils.logger import get_logger

logger = get_logger("mirofish.services.graphiti_builder")


class GraphitiGraphBuilder:
    """
    Servicio de construcción de grafos usando Graphiti + Neo4j.

    Provee la misma interfaz que GraphBuilderService (Zep) para que
    el API endpoint /api/graph/build funcione con ambos backends.

    Args:
        backend: Instancia de GraphitiBackend (inyectada por el factory)
    """

    def __init__(self, backend=None):
        self._backend = backend or get_memory_backend()

    @staticmethod
    def _normalize_text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            return " ".join(GraphitiGraphBuilder._normalize_text(v) for v in value.values())
        if isinstance(value, list):
            return " ".join(GraphitiGraphBuilder._normalize_text(v) for v in value)
        return str(value).strip().lower()

    @staticmethod
    def _split_pascal_case(value: str) -> List[str]:
        return [part.lower() for part in re.findall(r"[A-Z][a-z0-9]*", value or "")]

    @staticmethod
    def _project_for_graph(graph_id: str):
        for project in ProjectManager.list_projects(limit=500):
            if project.graph_id == graph_id:
                return project
        return None

    def _derive_entity_type(
        self,
        entity,
        ontology_entity_types: List[Dict[str, Any]],
    ) -> str:
        explicit_keys = [
            "entity_type",
            "type",
            "category",
            "classification",
            "kind",
            "persona_type",
        ]
        attributes = entity.attributes or {}
        labels = entity.labels or []
        label_candidates = [label for label in labels if label not in ["Entity", "Node"]]
        valid_type_names = {
            str(spec.get("name", "")).strip(): spec for spec in ontology_entity_types if spec.get("name")
        }
        lowered_name_map = {name.lower(): name for name in valid_type_names}

        for key in explicit_keys:
            raw_value = attributes.get(key)
            if not raw_value:
                continue
            normalized_value = str(raw_value).strip().lower()
            if normalized_value in lowered_name_map:
                return lowered_name_map[normalized_value]

        for label in label_candidates:
            if label in valid_type_names:
                return label

        haystack = " ".join(
            filter(
                None,
                [
                    self._normalize_text(entity.name),
                    self._normalize_text(entity.summary),
                    self._normalize_text(attributes),
                ],
            )
        )
        attr_keys = {str(key).strip().lower() for key, value in attributes.items() if value not in [None, "", []]}

        best_name = None
        best_score = 0
        for spec in ontology_entity_types:
            name = str(spec.get("name", "")).strip()
            if not name:
                continue

            score = 0
            attr_names = {
                str(attr.get("name", "")).strip().lower()
                for attr in spec.get("attributes", [])
                if attr.get("name")
            }
            if attr_names:
                score += len(attr_keys.intersection(attr_names)) * 3

            for example in spec.get("examples", []) or []:
                example_text = self._normalize_text(example)
                if example_text and (example_text in haystack or haystack in example_text):
                    score += 5

            type_tokens = self._split_pascal_case(name)
            if type_tokens and all(token in haystack for token in type_tokens):
                score += 3
            elif type_tokens and any(token in haystack for token in type_tokens):
                score += 1

            description = self._normalize_text(spec.get("description"))
            if description:
                desc_tokens = [token for token in re.findall(r"[a-zA-Z]{4,}", description)[:6]]
                overlap = sum(1 for token in desc_tokens if token.lower() in haystack)
                score += overlap

            if score > best_score:
                best_name = name
                best_score = score

        if best_name and best_score > 0:
            return best_name

        if "organization" in valid_type_names:
            org_markers = [
                "university",
                "company",
                "agency",
                "media",
                "hospital",
                "school",
                "platform",
                "foundation",
                "association",
                "group",
                "institut",
                "corp",
                "inc",
                "ltd",
            ]
            if any(marker in haystack for marker in org_markers):
                return "Organization"

        if "person" in lowered_name_map:
            return lowered_name_map["person"]
        if "organization" in lowered_name_map:
            return lowered_name_map["organization"]

        return entity.get_entity_type() or "Entity"

    def create_graph(self, name: str) -> str:
        """
        Crear un nuevo grafo en Graphiti.

        Args:
            name: Nombre del grafo

        Returns:
            graph_id del grafo creado
        """
        graph_id = f"mirofish_{uuid.uuid4().hex[:16]}"
        logger.info(f"Creando grafo Graphiti: {graph_id} ({name})")

        self._backend.create_graph(name=name, ontology=None)
        return graph_id

    def set_ontology(self, graph_id: str, ontology: Dict[str, Any]):
        """
        Configurar ontología del grafo (no-op en Graphiti).

        Graphiti extrae entidades y relaciones automáticamente de los
        episodios via LLM. No requiere definición previa de ontología.
        guardamos la ontología como propiedad del grafo para referencia.

        Args:
            graph_id: ID del grafo
            ontology: Definición de ontología (entity_types, edge_types)
        """
        logger.info(f"Graphiti: set_ontology no requerido, extracción automática")

        # Graphiti no tiene set_ontology - la ontología se maneja implicitamente
        # durante add_episode() via LLM entity extraction
        pass

    def add_text_batches(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 3,
        progress_callback: Optional[Callable] = None,
    ) -> List[str]:
        """
        Agregar texto al grafo en lotes via Graphiti add_episode.

        Args:
            graph_id: ID del grafo
            chunks: Lista de chunks de texto
            batch_size: Tamaño del lote (no relevante para Graphiti, se procesa uno por uno)
            progress_callback: Callback de progreso (msg, ratio)

        Returns:
            Lista de episode UUIDs
        """
        episode_uuids = []
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            batch_num = i + 1

            if progress_callback:
                progress = (i + 1) / total_chunks
                progress_callback(
                    f"Procesando chunk {batch_num}/{total_chunks}",
                    progress,
                )

            try:
                result = self._backend.add_episode(
                    graph_id=graph_id,
                    content=chunk,
                    reference_time=None,
                    name=f"Episode_{batch_num}",
                    source_type="text",
                )
                episode_uuids.append(result.episode_uuid)

            except Exception as e:
                logger.error(f"Error al agregar chunk {batch_num}: {str(e)}")
                raise

        return episode_uuids

    def _wait_for_episodes(
        self,
        episode_uuids: List[str],
        progress_callback: Optional[Callable] = None,
        timeout: int = 600,
    ):
        """
        Esperar a que todos los episodes se procesen.

        En Graphiti, add_episode es sincrono y retorna cuando el episode
        ya está procesado. No hay etapa asíncrona de procesamiento como en Zep.
        Esta método es un no-op para mantener compatibilidad de interfaz.

        Args:
            episode_uuids: Lista de UUIDs de episodes
            progress_callback: Callback de progreso
            timeout: Timeout en segundos (ignorado)
        """
        if not episode_uuids:
            if progress_callback:
                progress_callback("No episodes to wait for", 1.0)
            return

        if progress_callback:
            progress_callback(
                f"Graphiti: {len(episode_uuids)} episodes processed synchronously",
                1.0,
            )

    def get_graph_data(self, graph_id: str) -> Dict[str, Any]:
        """
        Obtener datos completos del grafo (nodos y bordes).

        Args:
            graph_id: ID del grafo

        Returns:
            Diccionario con nodes, edges y estadísticas
        """
        logger.info(f"Obteniendo datos del grafo {graph_id}")

        entities = self._backend.get_entities(graph_id=graph_id)
        edges = self._backend.get_edges(graph_id=graph_id)
        project = self._project_for_graph(graph_id)
        ontology_entity_types = ((project.ontology or {}).get("entity_types", []) if project else [])

        # Serializar nodos desde EntityNode objects
        nodes_data = []
        for entity in entities:
            entity_type = self._derive_entity_type(entity, ontology_entity_types)
            entity.entity_type = entity_type
            nodes_data.append(
                {
                    "uuid": entity.uuid,
                    "name": entity.name,
                    "labels": entity.labels or [],
                    "summary": entity.summary or "",
                    "attributes": entity.attributes or {},
                    "entity_type": entity_type,
                    "created_at": None,
                }
            )

        # Serializar bordes desde dicts
        edges_data = [
            {
                "uuid": edge.get("uuid", ""),
                "name": edge.get("name", ""),
                "fact": edge.get("fact", ""),
                "source_node_uuid": edge.get("source_node_uuid", ""),
                "target_node_uuid": edge.get("target_node_uuid", ""),
                "source_node_name": edge.get("source_node_name", ""),
                "target_node_name": edge.get("target_node_name", ""),
                "attributes": edge.get("attributes", {}),
                "created_at": edge.get("created_at"),
                "valid_at": edge.get("valid_at"),
                "invalid_at": edge.get("invalid_at"),
                "expired_at": edge.get("expired_at"),
            }
            for edge in edges
        ]

        return build_graph_data_response(graph_id, nodes_data, edges_data)

    def delete_graph(self, graph_id: str):
        """
        Eliminar el grafo de Graphiti.

        Args:
            graph_id: ID del grafo a eliminar
        """
        logger.info(f"Eliminando grafo {graph_id}")
        self._backend.delete_graph(graph_id)
