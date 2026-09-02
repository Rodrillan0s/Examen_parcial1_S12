class AppConfig {
    static const String apiBaseUrl = String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'https://taller-exa2-backend.onrender.com',
    );
}