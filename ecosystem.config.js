module.exports = {
    apps: [
        {
            name: 'agent-service',
            cwd: 'd:\\HSKGPT\\ChineseLearning\\agent_service',
            script: 'uvicorn',
            args: 'api:app --reload --port 8000',
            interpreter: 'python',
            env: {
                PYTHONUNBUFFERED: '1'
            }
        },
        {
            name: 'auth-service',
            cwd: 'd:\\HSKGPT\\ChineseLearning\\auth_service',
            script: 'uvicorn',
            args: 'api:app --reload --port 8001',
            interpreter: 'python',
            env: {
                PYTHONUNBUFFERED: '1'
            }
        }
    ]
};
