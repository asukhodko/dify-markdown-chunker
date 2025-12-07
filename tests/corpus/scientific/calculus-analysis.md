# Calculus and Mathematical Analysis

Essential formulas from differential and integral calculus.

## 1. Limits and Continuity

### 1.1 Definition of Limit

$$
\lim_{x \to a} f(x) = L \iff \forall \epsilon > 0, \exists \delta > 0 : 0 < |x-a| < \delta \Rightarrow |f(x) - L| < \epsilon
$$

### 1.2 Important Limits

**Fundamental limits:**
$$
\lim_{x \to 0} \frac{\sin x}{x} = 1
$$

$$
\lim_{x \to 0} \frac{1 - \cos x}{x^2} = \frac{1}{2}
$$

$$
\lim_{x \to 0} \frac{e^x - 1}{x} = 1
$$

$$
\lim_{x \to 0} \frac{\ln(1+x)}{x} = 1
$$

**Euler's number:**
$$
e = \lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n = \lim_{x \to 0} (1+x)^{1/x}
$$

### 1.3 L'Hôpital's Rule

If $\lim_{x \to a} f(x) = \lim_{x \to a} g(x) = 0$ or $\pm\infty$:
$$
\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)}
$$

---

## 2. Derivatives

### 2.1 Definition

$$
f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
$$

### 2.2 Basic Rules

**Sum rule:**
$$
(f + g)' = f' + g'
$$

**Product rule:**
$$
(fg)' = f'g + fg'
$$

**Quotient rule:**
$$
\left(\frac{f}{g}\right)' = \frac{f'g - fg'}{g^2}
$$

**Chain rule:**
$$
(f \circ g)'(x) = f'(g(x)) \cdot g'(x)
$$

### 2.3 Common Derivatives

| Function | Derivative |
|----------|------------|
| $x^n$ | $nx^{n-1}$ |
| $e^x$ | $e^x$ |
| $\ln x$ | $\frac{1}{x}$ |
| $\sin x$ | $\cos x$ |
| $\cos x$ | $-\sin x$ |
| $\tan x$ | $\sec^2 x$ |

### 2.4 Implicit Differentiation

For $F(x, y) = 0$:
$$
\frac{dy}{dx} = -\frac{\partial F/\partial x}{\partial F/\partial y} = -\frac{F_x}{F_y}
$$

---

## 3. Taylor Series

### 3.1 Taylor Expansion

$$
f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n
$$

**Maclaurin series** (Taylor at $a=0$):
$$
f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(0)}{n!}x^n
$$

### 3.2 Common Expansions

$$
e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots
$$

$$
\sin x = \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots
$$

$$
\cos x = \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n}}{(2n)!} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots
$$

$$
\ln(1+x) = \sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^n}{n} = x - \frac{x^2}{2} + \frac{x^3}{3} - \cdots
$$

### 3.3 Remainder Term

Lagrange form:
$$
R_n(x) = \frac{f^{(n+1)}(\xi)}{(n+1)!}(x-a)^{n+1}
$$

for some $\xi$ between $a$ and $x$.

---

## 4. Integration

### 4.1 Definite Integral

$$
\int_a^b f(x)\,dx = \lim_{n \to \infty} \sum_{i=1}^{n} f(x_i^*)\Delta x
$$

### 4.2 Fundamental Theorem of Calculus

**Part 1:**
$$
\frac{d}{dx}\int_a^x f(t)\,dt = f(x)
$$

**Part 2:**
$$
\int_a^b f(x)\,dx = F(b) - F(a)
$$

where $F'(x) = f(x)$

### 4.3 Integration Techniques

**Integration by parts:**
$$
\int u\,dv = uv - \int v\,du
$$

**Substitution:**
$$
\int f(g(x))g'(x)\,dx = \int f(u)\,du
$$

### 4.4 Common Integrals

$$
\int x^n \, dx = \frac{x^{n+1}}{n+1} + C, \quad n \neq -1
$$

$$
\int e^x \, dx = e^x + C
$$

$$
\int \frac{1}{x} \, dx = \ln|x| + C
$$

$$
\int \sin x \, dx = -\cos x + C
$$

$$
\int \frac{1}{1+x^2} \, dx = \arctan x + C
$$

$$
\int \frac{1}{\sqrt{1-x^2}} \, dx = \arcsin x + C
$$

---

## 5. Multivariable Calculus

### 5.1 Partial Derivatives

$$
\frac{\partial f}{\partial x} = \lim_{h \to 0} \frac{f(x+h, y) - f(x, y)}{h}
$$

### 5.2 Gradient

$$
\nabla f = \left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \ldots, \frac{\partial f}{\partial x_n}\right)
$$

### 5.3 Directional Derivative

$$
D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u} = |\nabla f| \cos \theta
$$

### 5.4 Chain Rule (Multivariable)

For $z = f(x, y)$ where $x = g(t)$ and $y = h(t)$:
$$
\frac{dz}{dt} = \frac{\partial f}{\partial x}\frac{dx}{dt} + \frac{\partial f}{\partial y}\frac{dy}{dt}
$$

### 5.5 Jacobian Matrix

For $\mathbf{f}: \mathbb{R}^n \to \mathbb{R}^m$:
$$
\mathbf{J} = \begin{pmatrix}
\frac{\partial f_1}{\partial x_1} & \cdots & \frac{\partial f_1}{\partial x_n} \\
\vdots & \ddots & \vdots \\
\frac{\partial f_m}{\partial x_1} & \cdots & \frac{\partial f_m}{\partial x_n}
\end{pmatrix}
$$

### 5.6 Hessian Matrix

$$
\mathbf{H}(f) = \begin{pmatrix}
\frac{\partial^2 f}{\partial x_1^2} & \frac{\partial^2 f}{\partial x_1 \partial x_2} & \cdots \\
\frac{\partial^2 f}{\partial x_2 \partial x_1} & \frac{\partial^2 f}{\partial x_2^2} & \cdots \\
\vdots & \vdots & \ddots
\end{pmatrix}
$$

---

## 6. Vector Calculus

### 6.1 Divergence

$$
\nabla \cdot \mathbf{F} = \frac{\partial F_x}{\partial x} + \frac{\partial F_y}{\partial y} + \frac{\partial F_z}{\partial z}
$$

### 6.2 Curl

$$
\nabla \times \mathbf{F} = \begin{vmatrix}
\mathbf{i} & \mathbf{j} & \mathbf{k} \\
\frac{\partial}{\partial x} & \frac{\partial}{\partial y} & \frac{\partial}{\partial z} \\
F_x & F_y & F_z
\end{vmatrix}
$$

### 6.3 Laplacian

$$
\nabla^2 f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2} + \frac{\partial^2 f}{\partial z^2}
$$

### 6.4 Integral Theorems

**Green's Theorem:**
$$
\oint_C (P\,dx + Q\,dy) = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right) dA
$$

**Stokes' Theorem:**
$$
\oint_C \mathbf{F} \cdot d\mathbf{r} = \iint_S (\nabla \times \mathbf{F}) \cdot d\mathbf{S}
$$

**Divergence Theorem:**
$$
\iint_S \mathbf{F} \cdot d\mathbf{S} = \iiint_V (\nabla \cdot \mathbf{F}) \, dV
$$

---

## 7. Differential Equations

### 7.1 First-Order Linear ODE

Form: $y' + P(x)y = Q(x)$

**Solution:**
$$
y = e^{-\int P\,dx}\left(\int Q e^{\int P\,dx}\,dx + C\right)
$$

### 7.2 Second-Order Linear ODE

Form: $ay'' + by' + cy = 0$

Characteristic equation: $ar^2 + br + c = 0$

**General solution:**
- Distinct real roots $r_1, r_2$: $y = C_1 e^{r_1 x} + C_2 e^{r_2 x}$
- Repeated root $r$: $y = (C_1 + C_2 x)e^{rx}$
- Complex roots $\alpha \pm \beta i$: $y = e^{\alpha x}(C_1 \cos\beta x + C_2 \sin\beta x)$
