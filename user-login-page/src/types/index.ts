export interface UserCredentials {
    username: string;
    password: string;
}

export interface LoginFormProps {
    onSubmit: (credentials: UserCredentials) => void;
}