/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  // より多くの環境変数をここに追加できます
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 