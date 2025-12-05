"""Configuration for corpus builder."""

from pathlib import Path

# Paths
WORKSPACE_ROOT = Path("/home/dalamar81/git/dify-markdown-chunker.qoder")
CORPUS_ROOT = WORKSPACE_ROOT / "tests" / "corpus"

# Target counts per category
TARGETS = {
    "technical_docs": {
        "total": 100,
        "subcategories": {
            "kubernetes": 25,
            "docker": 25,
            "react": 25,
            "aws": 25,
        },
    },
    "github_readmes": {
        "total": 100,
        "subcategories": {
            "python": 25,
            "javascript": 25,
            "go": 25,
            "rust": 25,
        },
    },
    "changelogs": {"total": 50},
    "engineering_blogs": {"total": 50},
    "personal_notes": {
        "total": 30,
        "subcategories": {
            "unstructured": 10,
            "journals": 10,
            "cheatsheets": 10,
        },
    },
    "debug_logs": {"total": 20},
    "nested_fencing": {"total": 20},
    "research_notes": {"total": 20},
    "mixed_content": {"total": 20},
}

# Size distribution targets
SIZE_DISTRIBUTION = {
    "tiny": {"range": (0, 1024), "count": 20},
    "small": {"range": (1024, 5120), "count": 80},
    "medium": {"range": (5120, 20480), "count": 160},
    "large": {"range": (20480, 102400), "count": 120},
    "very_large": {"range": (102400, float("inf")), "count": 30},
}

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"

# Top repositories per language
GITHUB_REPOS = {
    "python": [
        "tensorflow/tensorflow",
        "pytorch/pytorch",
        "django/django",
        "pallets/flask",
        "psf/requests",
        "scikit-learn/scikit-learn",
        "pandas-dev/pandas",
        "numpy/numpy",
        "fastapi/fastapi",
        "ansible/ansible",
        "scrapy/scrapy",
        "certbot/certbot",
        "python/cpython",
        "tornadoweb/tornado",
        "ytdl-org/youtube-dl",
        "ageitgey/face_recognition",
        "explosion/spaCy",
        "streamlit/streamlit",
        "celery/celery",
        "boto/boto3",
        "conda/conda",
        "pallets/click",
        "psf/black",
        "sqlalchemy/sqlalchemy",
        "keras-team/keras",
    ],
    "javascript": [
        "facebook/react",
        "vuejs/vue",
        "angular/angular",
        "vercel/next.js",
        "expressjs/express",
        "webpack/webpack",
        "nodejs/node",
        "microsoft/TypeScript",
        "mrdoob/three.js",
        "chartjs/Chart.js",
        "axios/axios",
        "mui/material-ui",
        "prettier/prettier",
        "lodash/lodash",
        "moment/moment",
        "electron/electron",
        "socketio/socket.io",
        "meteor/meteor",
        "nuxt/nuxt",
        "strapi/strapi",
        "tailwindlabs/tailwindcss",
        "vitejs/vite",
        "parcel-bundler/parcel",
        "babel/babel",
        "eslint/eslint",
    ],
    "go": [
        "kubernetes/kubernetes",
        "moby/moby",
        "gohugoio/hugo",
        "gin-gonic/gin",
        "spf13/cobra",
        "prometheus/prometheus",
        "etcd-io/etcd",
        "traefik/traefik",
        "grafana/grafana",
        "influxdata/influxdb",
        "helm/helm",
        "minio/minio",
        "hashicorp/terraform",
        "hashicorp/consul",
        "hashicorp/vault",
        "containerd/containerd",
        "CodisLabs/codis",
        "beego/beego",
        "go-kit/kit",
        "go-gitea/gitea",
        "syncthing/syncthing",
        "rclone/rclone",
        "urfave/cli",
        "gorilla/mux",
        "labstack/echo",
    ],
    "rust": [
        "rust-lang/rust",
        "denoland/deno",
        "BurntSushi/ripgrep",
        "alacritty/alacritty",
        "sharkdp/bat",
        "tokio-rs/tokio",
        "rust-lang/cargo",
        "tauri-apps/tauri",
        "servo/servo",
        "swc-project/swc",
        "actix/actix-web",
        "firecracker-microvm/firecracker",
        "tikv/tikv",
        "yewstack/yew",
        "starship/starship",
        "sharkdp/fd",
        "dandavison/delta",
        "ogham/exa",
        "Wilfred/difftastic",
        "zellij-org/zellij",
        "nushell/nushell",
        "helix-editor/helix",
        "rome/tools",
        "rustdesk/rustdesk",
        "meilisearch/meilisearch",
    ],
}

# Documentation sources
DOCS_SOURCES = {
    "kubernetes": {
        "base_url": "https://kubernetes.io/docs/",
        "pages": [
            "concepts/overview/what-is-kubernetes/",
            "concepts/architecture/nodes/",
            "concepts/workloads/pods/",
            "concepts/services-networking/service/",
            "concepts/storage/volumes/",
            "tasks/configure-pod-container/configure-pod-configmap/",
            "tasks/run-application/run-stateless-application-deployment/",
            "reference/kubectl/cheatsheet/",
            "concepts/cluster-administration/networking/",
            "concepts/policy/resource-quotas/",
        ],
    },
    "docker": {
        "base_url": "https://docs.docker.com/",
        "pages": [
            "get-started/",
            "engine/reference/builder/",
            "compose/compose-file/",
            "storage/volumes/",
            "network/",
            "engine/swarm/",
            "develop/develop-images/dockerfile_best-practices/",
        ],
    },
    "react": {
        "github_repo": "reactjs/react.dev",
        "path": "src/content/learn",
    },
    "aws": {
        "github_repo": "awsdocs/amazon-ec2-user-guide",
        "path": "doc_source",
    },
}

# Engineering blog sources
BLOG_SOURCES = [
    "https://netflixtechblog.com/",
    "https://eng.uber.com/",
    "https://medium.com/airbnb-engineering",
    "https://stripe.com/blog/engineering",
    "https://blog.cloudflare.com/",
    "https://github.blog/engineering/",
    "https://dropbox.tech/",
    "https://shopify.engineering/",
    "https://engineeringblog.yelp.com/",
    "https://instagram-engineering.com/",
]

# Rate limiting
GITHUB_RATE_LIMIT_DELAY = 1.0  # seconds between requests
WEB_SCRAPE_DELAY = 2.0  # seconds between web scrapes

# Generation parameters
SYNTHETIC_TOPICS = {
    "programming": [
        "Python",
        "JavaScript",
        "Go",
        "Rust",
        "TypeScript",
        "Java",
        "C++",
        "SQL",
    ],
    "tools": [
        "Git",
        "Docker",
        "Kubernetes",
        "Vim",
        "Bash",
        "PostgreSQL",
        "Redis",
        "nginx",
    ],
    "concepts": [
        "async/await",
        "REST APIs",
        "GraphQL",
        "microservices",
        "databases",
        "caching",
        "testing",
        "CI/CD",
    ],
}

# Validation thresholds
VALIDATION = {
    "min_total_files": 400,
    "size_distribution_tolerance": 0.05,  # ±5%
    "characteristic_tolerance": 0.10,  # ±10%
    "min_unique_ratio": 1.0,  # 100% unique
}
