# Machine Learning Mathematical Foundations

This document covers essential mathematical equations used in machine learning, including distance measures, loss functions, and generative model formulations.

## 1. Distance Measures

### 1.1 Kullback-Leibler Divergence (KL-Divergence)

KL-Divergence measures how one probability distribution diverges from a second expected probability distribution:

$$
KL(P||Q) = \sum_{x} P(x) \log\left(\frac{P(x)}{Q(x)}\right)
$$

For continuous distributions:

$$
KL(P||Q) = \int_{-\infty}^{\infty} p(x) \log\left(\frac{p(x)}{q(x)}\right) dx
$$

**Properties:**
- Non-negative: $KL(P||Q) \geq 0$
- Asymmetric: $KL(P||Q) \neq KL(Q||P)$
- Zero iff $P = Q$

### 1.2 Jensen-Shannon Divergence (JS-Divergence)

A symmetric version of KL-Divergence:

$$
JS(P||Q) = \frac{1}{2}KL\left(P||\frac{P+Q}{2}\right) + \frac{1}{2}KL\left(Q||\frac{P+Q}{2}\right)
$$

This is bounded: $0 \leq JS(P||Q) \leq \log 2$

### 1.3 Wasserstein Distance (Optimal Transport)

Also known as Earth Mover's Distance:

$$
W_{p}(P,Q) = \left(\inf_{J \in \mathcal{J}(P,Q)} \int ||x-y||^{p} dJ(x,y)\right)^{\frac{1}{p}}
$$

For $p=1$, this simplifies to:

$$
W_1(P,Q) = \inf_{\gamma \in \Pi(P,Q)} \mathbb{E}_{(x,y) \sim \gamma}[||x - y||]
$$

### 1.4 Maximum Mean Discrepancy (MMD)

A kernel-based distance measure:

$$
\text{MMD}(\mathcal{F}, X, Y) := \sup_{f \in \mathcal{F}} \left(\frac{1}{m}\sum_{i=1}^{m} f(x_i) - \frac{1}{n}\sum_{j=1}^{n} f(y_j)\right)
$$

With kernel $k$:

$$
\text{MMD}^2 = \mathbb{E}[k(x,x')] - 2\mathbb{E}[k(x,y)] + \mathbb{E}[k(y,y')]
$$

### 1.5 Mahalanobis Distance

Distance accounting for correlations in the data:

$$
D_M(x, y) = \sqrt{(x-y)^T \Sigma^{-1} (x-y)}
$$

where $\Sigma$ is the covariance matrix.

---

## 2. Generative Models

### 2.1 Generative Adversarial Networks (GAN)

The minimax objective for GANs:

$$
\min_G \max_D V(D,G) = \mathbb{E}_{x \sim p_{data}(x)}[\log D(x)] + \mathbb{E}_{z \sim p_z(z)}[\log(1-D(G(z)))]
$$

**Optimal discriminator:**

$$
D^*(x) = \frac{p_{data}(x)}{p_{data}(x) + p_g(x)}
$$

**Generator loss (non-saturating):**

$$
\mathcal{L}_G = -\mathbb{E}_{z \sim p_z(z)}[\log D(G(z))]
$$

### 2.2 Variational AutoEncoder (VAE)

#### Evidence Lower Bound (ELBO)

$$
\mathcal{L}_{\theta,\phi}(\mathbf{x}) = \mathbb{E}_{q_\phi(\mathbf{z}|\mathbf{x})}[\log p_\theta(\mathbf{x},\mathbf{z}) - \log q_\phi(\mathbf{z}|\mathbf{x})]
$$

Equivalently:

$$
\log p_\theta(\mathbf{x}) \geq \mathbb{E}_{q_\phi(\mathbf{z}|\mathbf{x})}[\log p_\theta(\mathbf{x}|\mathbf{z})] - D_{KL}(q_\phi(\mathbf{z}|\mathbf{x}) || p(\mathbf{z}))
$$

#### Reparameterization Trick

$$
\mathbf{z} = \boldsymbol{\mu} + \boldsymbol{\sigma} \odot \boldsymbol{\epsilon}, \quad \boldsymbol{\epsilon} \sim \mathcal{N}(0, I)
$$

### 2.3 Diffusion Models (DDPM)

#### Forward Process

$$
q(x_t|x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t}x_{t-1}, \beta_t I)
$$

$$
q(x_{1:T}|x_0) = \prod_{t=1}^{T} q(x_t|x_{t-1})
$$

#### Reparameterization

$$
x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1-\bar{\alpha}_t} \epsilon
$$

where $\alpha_t = 1 - \beta_t$ and $\bar{\alpha}_t = \prod_{s=1}^{t} \alpha_s$

#### Reverse Process

$$
p_\theta(\mathbf{x}_{0:T}) = p(\mathbf{x}_T) \prod_{t=1}^{T} p_\theta(\mathbf{x}_{t-1}|\mathbf{x}_t)
$$

$$
p_\theta(\mathbf{x}_{t-1}|\mathbf{x}_t) = \mathcal{N}(\mathbf{x}_{t-1}; \boldsymbol{\mu}_\theta(\mathbf{x}_t, t), \boldsymbol{\Sigma}_\theta(\mathbf{x}_t, t))
$$

#### Training Objective

\begin{align}
L_{simple} &= \mathbb{E}_{t, x_0, \epsilon}\left[||\epsilon - \epsilon_\theta(x_t, t)||^2\right]
\end{align}

---

## 3. Loss Functions

### 3.1 Cross-Entropy Loss

For binary classification:

$$
\mathcal{L}_{BCE} = -\frac{1}{N}\sum_{i=1}^{N}[y_i \log(\hat{y}_i) + (1-y_i)\log(1-\hat{y}_i)]
$$

For multi-class:

$$
\mathcal{L}_{CE} = -\sum_{c=1}^{C} y_c \log(\hat{y}_c)
$$

### 3.2 Mean Squared Error

$$
\mathcal{L}_{MSE} = \frac{1}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)^2
$$

### 3.3 Focal Loss

For handling class imbalance:

$$
FL(p_t) = -\alpha_t (1-p_t)^\gamma \log(p_t)
$$

---

## 4. Optimization

### 4.1 Gradient Descent

$$
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
$$

### 4.2 Adam Optimizer

\begin{align}
m_t &= \beta_1 m_{t-1} + (1-\beta_1) g_t \\
v_t &= \beta_2 v_{t-1} + (1-\beta_2) g_t^2 \\
\hat{m}_t &= \frac{m_t}{1-\beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t} \\
\theta_{t+1} &= \theta_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t
\end{align}

---

## 5. Neural Network Components

### 5.1 Softmax Function

$$
\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}
$$

### 5.2 Attention Mechanism

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

### 5.3 Layer Normalization

$$
\text{LayerNorm}(x) = \gamma \cdot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta
$$

where $\mu = \frac{1}{H}\sum_{i=1}^{H} x_i$ and $\sigma^2 = \frac{1}{H}\sum_{i=1}^{H}(x_i - \mu)^2$
