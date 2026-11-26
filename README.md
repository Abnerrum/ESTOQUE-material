# Controle de materiais — protótipo
Aplicação independente Flask para cadastro de materiais e solicitações. Configure ADMIN_PASSWORD, SECRET_KEY, STOCK_EMAIL e SMTP antes de usar. Não envie dados corporativos ou credenciais ao GitHub. SQLite precisa de disco persistente em produção. Autenticação corporativa e aprovação de TI são necessárias antes de uso real.

Build: `pip install -r requirements.txt`
Start: `gunicorn app:app`
