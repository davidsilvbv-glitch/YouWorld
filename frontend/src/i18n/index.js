import { createI18n } from 'vue-i18n'
import languages from '../../../locales/languages.json'

const localeFiles = import.meta.glob('../../../locales/!(languages).json', { eager: true })

const messages = {}
const availableLocales = []

for (const path in localeFiles) {
  const key = path.match(/\/([^/]+)\.json$/)[1]
  if (languages[key]) {
    messages[key] = localeFiles[path].default
    availableLocales.push({ key, label: languages[key].label })
  }
}

const authFallbacks = {
  es: {
    auth: {
      cta: 'Iniciar sesion',
      screenEyebrow: 'Acceso seguro',
      title: 'Inicia sesion para activar el motor',
      welcomeTitle: 'Sesion lista para continuar',
      description:
        'Puedes explorar la interfaz, cargar documentos y preparar tu prompt primero. Cuando quieras ejecutar la simulacion, entraras por esta misma puerta.',
      startRestriction:
        'Tu prompt y tus archivos ya quedaron listos. Para iniciar el motor necesitas entrar con tu cuenta y YouWorld continuara desde aqui.',
      googleButton: 'Continuar con Google',
      googleUnavailable:
        'Falta configurar VITE_GOOGLE_CLIENT_ID para mostrar el acceso con Google.',
      helper:
        'Accede o registrate con Google para guardar propiedad de tus proyectos y seguir el flujo completo.',
      loadingSession: 'Verificando sesion...',
      loggedInAs: 'Sesion iniciada como',
      loggedInText:
        'Ya tienes una sesion activa. Puedes seguir al inicio o continuar directamente con el siguiente paso bloqueado.',
      continueToEngine: 'Continuar al motor',
      continueToHome: 'Continuar a YouWorld',
      logout: 'Cerrar sesion',
      sessionFailed: 'No se pudo iniciar sesion en este momento.',
      googleCredentialMissing: 'Google no devolvio una credencial valida.'
    }
  },
  en: {
    auth: {
      cta: 'Sign in',
      screenEyebrow: 'Secure access',
      title: 'Sign in to activate the engine',
      welcomeTitle: 'Session ready to continue',
      description:
        'You can explore the interface, upload documents, and prepare your prompt first. When you are ready to run the simulation, this is the same doorway you will use.',
      startRestriction:
        'Your prompt and files are already staged. To start the engine you need to sign in and YouWorld will continue from here.',
      googleButton: 'Continue with Google',
      googleUnavailable:
        'VITE_GOOGLE_CLIENT_ID still needs to be configured to show Google sign-in.',
      helper:
        'Use Google to sign in or register so YouWorld can attach projects to your account.',
      loadingSession: 'Checking session...',
      loggedInAs: 'Signed in as',
      loggedInText:
        'You already have an active session. You can go back home or continue directly to the blocked step.',
      continueToEngine: 'Continue to engine',
      continueToHome: 'Continue to YouWorld',
      logout: 'Sign out',
      sessionFailed: 'Could not sign you in right now.',
      googleCredentialMissing: 'Google did not return a valid credential.'
    }
  }
}

for (const [localeKey, extra] of Object.entries(authFallbacks)) {
  if (messages[localeKey]) {
    messages[localeKey] = {
      ...messages[localeKey],
      ...extra
    }
  }
}

const savedLocale = localStorage.getItem('locale') || 'es'

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: savedLocale,
  fallbackLocale: 'es',
  messages
})

export { availableLocales }
export default i18n
