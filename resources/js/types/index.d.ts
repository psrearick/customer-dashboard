export interface User {
    id: number;
    name: string;
    email: string;
    email_verified_at?: string | null;
}

export interface FlashMessages {
    success?: string;
    error?: string;
    warning?: string;
    info?: string;
}

export interface AppInfo {
    name: string;
    version: string;
    environment: string;
}

export type PageProps<
    T extends Record<string, unknown> = Record<string, unknown>,
> = T & {
    auth: {
        user: User | null;
    };
    csrf_token: string;
    flash: FlashMessages;
    app: AppInfo;
};

declare global {
    interface ImportMetaEnv {
        readonly VITE_APP_NAME: string;
    }
}