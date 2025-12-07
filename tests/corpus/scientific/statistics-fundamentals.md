# Statistical Inference and Probability Theory

A comprehensive reference for fundamental statistical formulas and probability theory.

## 1. Descriptive Statistics

### 1.1 Measures of Central Tendency

**Arithmetic Mean:**

For discrete data:
$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
$$

For continuous data with density $f(x)$:
$$
\mu = \mathbb{E}[X] = \int_{-\infty}^{\infty} x \cdot f(x) \, dx
$$

**Weighted Mean:**
$$
\bar{x}_w = \frac{\sum_{i=1}^{n} w_i x_i}{\sum_{i=1}^{n} w_i}
$$

**Geometric Mean:**
$$
\bar{x}_g = \left(\prod_{i=1}^{n} x_i\right)^{1/n} = \exp\left(\frac{1}{n}\sum_{i=1}^{n} \ln x_i\right)
$$

### 1.2 Measures of Dispersion

**Variance:**

Population variance:
$$
\sigma^2 = \mathbb{E}[(X-\mu)^2] = \mathbb{E}[X^2] - (\mathbb{E}[X])^2
$$

Sample variance (unbiased):
$$
s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2
$$

**Standard Deviation:**
$$
\sigma = \sqrt{\sigma^2}, \quad s = \sqrt{s^2}
$$

**Coefficient of Variation:**
$$
CV = \frac{\sigma}{\mu} \times 100\%
$$

### 1.3 Higher Moments

**Skewness (Fisher):**
$$
\gamma_1 = \frac{\mathbb{E}[(X-\mu)^3]}{\sigma^3} = \frac{\mu_3}{\sigma^3}
$$

**Kurtosis:**
$$
\gamma_2 = \frac{\mathbb{E}[(X-\mu)^4]}{\sigma^4} - 3 = \frac{\mu_4}{\sigma^4} - 3
$$

---

## 2. Probability Distributions

### 2.1 Discrete Distributions

**Binomial Distribution:**
$$
P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}
$$

where $\mathbb{E}[X] = np$ and $\text{Var}(X) = np(1-p)$

**Poisson Distribution:**
$$
P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}
$$

where $\mathbb{E}[X] = \lambda$ and $\text{Var}(X) = \lambda$

**Geometric Distribution:**
$$
P(X=k) = (1-p)^{k-1} p
$$

### 2.2 Continuous Distributions

**Normal (Gaussian) Distribution:**
$$
f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)
$$

Standard normal:
$$
\phi(z) = \frac{1}{\sqrt{2\pi}} e^{-z^2/2}
$$

**Exponential Distribution:**
$$
f(x) = \lambda e^{-\lambda x}, \quad x \geq 0
$$

**Chi-Square Distribution:**
$$
f(x; k) = \frac{x^{k/2-1} e^{-x/2}}{2^{k/2} \Gamma(k/2)}, \quad x > 0
$$

**Student's t-Distribution:**
$$
f(t) = \frac{\Gamma\left(\frac{
u+1}{2}\right)}{\sqrt{
u\pi}\,\Gamma\left(\frac{
u}{2}\right)} \left(1 + \frac{t^2}{
u}\right)^{-\frac{
u+1}{2}}
$$

**F-Distribution:**
$$
f(x; d_1, d_2) = \frac{\sqrt{\frac{(d_1 x)^{d_1} d_2^{d_2}}{(d_1 x + d_2)^{d_1+d_2}}}}{x \cdot B\left(\frac{d_1}{2}, \frac{d_2}{2}\right)}
$$

---

## 3. Hypothesis Testing

### 3.1 Z-Test

Test statistic:
$$
z = \frac{\bar{x} - \mu_0}{\sigma/\sqrt{n}}
$$

### 3.2 T-Test

**One-sample t-test:**
$$
t = \frac{\bar{x} - \mu_0}{s/\sqrt{n}}
$$

**Two-sample t-test (pooled variance):**
$$
t = \frac{\bar{x}_1 - \bar{x}_2}{s_p\sqrt{\frac{1}{n_1} + \frac{1}{n_2}}}
$$

where pooled standard deviation:
$$
s_p = \sqrt{\frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}}
$$

### 3.3 Chi-Square Test

$$
\chi^2 = \sum_{i=1}^{k} \frac{(O_i - E_i)^2}{E_i}
$$

### 3.4 F-Test

$$
F = \frac{s_1^2}{s_2^2}
$$

---

## 4. Confidence Intervals

### 4.1 For Population Mean

When $\sigma$ is known:
$$
\bar{x} \pm z_{\alpha/2} \cdot \frac{\sigma}{\sqrt{n}}
$$

When $\sigma$ is unknown:
$$
\bar{x} \pm t_{\alpha/2, n-1} \cdot \frac{s}{\sqrt{n}}
$$

### 4.2 For Population Proportion

$$
\hat{p} \pm z_{\alpha/2} \sqrt{\frac{\hat{p}(1-\hat{p})}{n}}
$$

---

## 5. Regression Analysis

### 5.1 Simple Linear Regression

Model: $Y = \beta_0 + \beta_1 X + \epsilon$

**Least Squares Estimators:**
$$
\hat{\beta}_1 = \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^{n}(x_i - \bar{x})^2} = \frac{S_{xy}}{S_{xx}}
$$

$$
\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}
$$

### 5.2 Coefficient of Determination

$$
R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}
$$

### 5.3 Multiple Linear Regression

In matrix form:
$$
\hat{\boldsymbol{\beta}} = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}
$$

---

## 6. Correlation

### 6.1 Pearson Correlation Coefficient

$$
r = \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i - \bar{x})^2}\sqrt{\sum_{i=1}^{n}(y_i - \bar{y})^2}}
$$

Or equivalently:
$$
r = \frac{n\sum x_i y_i - \sum x_i \sum y_i}{\sqrt{n\sum x_i^2 - (\sum x_i)^2}\sqrt{n\sum y_i^2 - (\sum y_i)^2}}
$$

### 6.2 Spearman Rank Correlation

$$
\rho = 1 - \frac{6\sum d_i^2}{n(n^2-1)}
$$

where $d_i = \text{rank}(x_i) - \text{rank}(y_i)$

---

## 7. Bayesian Statistics

### 7.1 Bayes' Theorem

$$
P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}
$$

For continuous parameters:
$$
p(\theta|x) = \frac{p(x|\theta) \cdot p(\theta)}{p(x)} = \frac{p(x|\theta) \cdot p(\theta)}{\int p(x|\theta) p(\theta) d\theta}
$$

### 7.2 Posterior Predictive Distribution

$$
p(\tilde{x}|x) = \int p(\tilde{x}|\theta) p(\theta|x) d\theta
$$

---

## 8. Maximum Likelihood Estimation

### 8.1 Likelihood Function

$$
\mathcal{L}(\theta) = \prod_{i=1}^{n} f(x_i|\theta)
$$

### 8.2 Log-Likelihood

$$
\ell(\theta) = \sum_{i=1}^{n} \log f(x_i|\theta)
$$

### 8.3 MLE Condition

$$
\frac{\partial \ell(\theta)}{\partial \theta} = 0
$$

### 8.4 Fisher Information

$$
I(\theta) = -\mathbb{E}\left[\frac{\partial^2 \ell(\theta)}{\partial \theta^2}\right]
$$

Cramér-Rao Lower Bound:
$$
\text{Var}(\hat{\theta}) \geq \frac{1}{n \cdot I(\theta)}
$$
