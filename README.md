# 🎬 Sistema de Gestão de Filmes — API (Back-end)

Projeto de API REST desenvolvido como MVP para a disciplina **Desenvolvimento Full Stack Avançado** da PUC-Rio.

---

## 🎯 Objetivo

Apresentar o comportamento da arquitetura de uma API REST e demonstrar como o Back-end atua como o núcleo de processamento, comunicando-se simultaneamente com:

- 🖥️ **Interface (Front-end):** Provendo os dados necessários para a experiência do usuário.
- 🎥 **API Externa (TMDB):** Realizando a ponte para busca de dados dinâmicos e metadados de filmes em tempo real através do The Movie Database (TMDB).
- 🗄️ **Persistência Local (SQLite):** Garantindo o armazenamento seguro das regras de negócio e cadastros de clientes.

---

## 🛠️ Tecnologias Utilizadas

- 🐍 **Python 3.x & Flask:** Micro-framework para a construção da API.
- 🔗 **SQLAlchemy:** ORM para abstração e manipulação do banco de dados.
- 🗃️ **SQLite:** Banco de dados relacional (persistência dos cadastros dos clientes).
- 📄 **OpenAPI 3 / Swagger:** Documentação interativa da API.
- 🐳 **Docker:** Containerização para garantir a portabilidade do ambiente.

---

## 🏗️ Comportamento da Arquitetura

A API foi desenhada para seguir os princípios REST, garantindo que:

- 🔄 **Integração com TMDB:** O sistema realiza requisições HTTP para a API externa do TMDB para alimentar o catálogo de filmes, garantindo dados sempre atualizados sem necessidade de armazenamento local massivo.
- 📦 **Padronização:** As respostas são entregues em formato JSON, facilitando o consumo pelo Front-end que roda de forma independente.

---

## 🚀 Execução (via Docker)

Para garantir que a arquitetura funcione conforme desenhada, utilize o Docker para subir o serviço.

**🔨 Construir a imagem:**
```bash
docker build -t locadora-backend .
```

**▶️ Executar o container:**
```bash
docker run -p 5001:5000 locadora-backend
```

### Via Docker Compose

```bash
docker-compose up --build
```

---

## 📖 Documentação Interativa (Swagger)

A documentação da arquitetura e dos contratos da API (OpenAPI 3) pode ser acessada em tempo de execução:

[http://localhost:5001/#/](http://localhost:5001/#/)
