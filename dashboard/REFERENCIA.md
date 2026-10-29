Infraestrutura adaptada do laboratório DB L03: https://gitlab.com/gilbriatore/2026/database/analytics-bi-redash.git

Porta MongoDB alterada para 27018 no host para coexistir com o serviço nativo. A porta interna permanece 27017. A imagem Redash é a mesma do laboratório.

Preparação, em um Docker funcional, dentro de dashboard/: copiar .env.example para .env e definir chaves locais; docker compose up -d mongodb postgres redis; docker compose run --rm server create_db (somente para volume novo); docker compose up -d server worker scheduler. Abra http://localhost:5000 e crie a conta administrativa.

Depois, a partir da raiz do projeto: python importar_mongo_redash.py --destino mongodb://127.0.0.1:27018. No Redash, configurar mongodb://mongodb:27017/n2_equipe10.

Parar preservando volumes: docker compose stop. Não utilizar down -v para encerrar a apresentação.

Nenhum desses serviços foi declarado funcional nesta máquina: o Docker Desktop falha antes de iniciar os contêineres.
