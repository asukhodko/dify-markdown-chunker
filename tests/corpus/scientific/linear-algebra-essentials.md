# Linear Algebra Essentials

Core concepts and formulas from linear algebra for machine learning and scientific computing.

## 1. Vectors and Vector Spaces

### 1.1 Vector Operations

**Dot product:**
$$
\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i = |\mathbf{a}||\mathbf{b}|\cos\theta
$$

**Cross product** (in $\mathbb{R}^3$):
$$
\mathbf{a} \times \mathbf{b} = \begin{vmatrix}
\mathbf{i} & \mathbf{j} & \mathbf{k} \\
a_1 & a_2 & a_3 \\
b_1 & b_2 & b_3
\end{vmatrix}
$$

### 1.2 Norms

**$L^p$ norm:**
$$
||\mathbf{x}||_p = \left(\sum_{i=1}^{n} |x_i|^p\right)^{1/p}
$$

**Common norms:**
$$
||\mathbf{x}||_1 = \sum_{i=1}^{n} |x_i| \quad \text{(Manhattan)}
$$

$$
||\mathbf{x}||_2 = \sqrt{\sum_{i=1}^{n} x_i^2} \quad \text{(Euclidean)}
$$

$$
||\mathbf{x}||_\infty = \max_i |x_i| \quad \text{(Chebyshev)}
$$

### 1.3 Projections

Projection of $\mathbf{b}$ onto $\mathbf{a}$:
$$
\text{proj}_{\mathbf{a}}\mathbf{b} = \frac{\mathbf{a} \cdot \mathbf{b}}{||\mathbf{a}||^2}\mathbf{a}
$$

Projection onto subspace spanned by columns of $A$:
$$
\text{proj}_A \mathbf{b} = A(A^TA)^{-1}A^T\mathbf{b}
$$

---

## 2. Matrices

### 2.1 Matrix Operations

**Matrix-vector multiplication:**
$$
(A\mathbf{x})_i = \sum_{j=1}^{n} A_{ij}x_j
$$

**Matrix-matrix multiplication:**
$$
(AB)_{ij} = \sum_{k=1}^{m} A_{ik}B_{kj}
$$

### 2.2 Special Matrices

**Identity matrix:**
$$
I = \begin{pmatrix} 1 & 0 & \cdots & 0 \\ 0 & 1 & \cdots & 0 \\ \vdots & \vdots & \ddots & \vdots \\ 0 & 0 & \cdots & 1 \end{pmatrix}
$$

**Diagonal matrix:**
$$
D = \text{diag}(d_1, d_2, \ldots, d_n)
$$

**Symmetric:** $A = A^T$

**Orthogonal:** $Q^TQ = QQ^T = I$

**Positive definite:** $\mathbf{x}^T A \mathbf{x} > 0$ for all $\mathbf{x} \neq 0$

### 2.3 Matrix Norms

**Frobenius norm:**
$$
||A||_F = \sqrt{\sum_{i=1}^{m}\sum_{j=1}^{n} |a_{ij}|^2} = \sqrt{\text{tr}(A^T A)}
$$

**Spectral norm:**
$$
||A||_2 = \sigma_{\max}(A) = \sqrt{\lambda_{\max}(A^T A)}
$$

---

## 3. Determinants and Inverses

### 3.1 Determinant Properties

$$
\det(AB) = \det(A)\det(B)
$$

$$
\det(A^{-1}) = \frac{1}{\det(A)}
$$

$$
\det(A^T) = \det(A)
$$

$$
\det(cA) = c^n \det(A) \quad \text{for } A \in \mathbb{R}^{n \times n}
$$

### 3.2 2×2 Matrix

$$
A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}
$$

$$
\det(A) = ad - bc
$$

$$
A^{-1} = \frac{1}{ad-bc}\begin{pmatrix} d & -b \\ -c & a \end{pmatrix}
$$

### 3.3 General Inverse

$$
A^{-1} = \frac{1}{\det(A)} \text{adj}(A)
$$

where $\text{adj}(A)$ is the adjugate (transpose of cofactor matrix).

### 3.4 Sherman-Morrison Formula

$$
(A + \mathbf{u}\mathbf{v}^T)^{-1} = A^{-1} - \frac{A^{-1}\mathbf{u}\mathbf{v}^T A^{-1}}{1 + \mathbf{v}^T A^{-1}\mathbf{u}}
$$

---

## 4. Eigenvalues and Eigenvectors

### 4.1 Definition

For matrix $A$:
$$
A\mathbf{v} = \lambda\mathbf{v}
$$

where $\lambda$ is an eigenvalue and $\mathbf{v}$ is the corresponding eigenvector.

### 4.2 Characteristic Equation

$$
\det(A - \lambda I) = 0
$$

### 4.3 Properties

$$
\text{tr}(A) = \sum_{i=1}^{n} \lambda_i
$$

$$
\det(A) = \prod_{i=1}^{n} \lambda_i
$$

### 4.4 Eigendecomposition

For diagonalizable matrix:
$$
A = V\Lambda V^{-1}
$$

where $V$ contains eigenvectors and $\Lambda = \text{diag}(\lambda_1, \ldots, \lambda_n)$

**Matrix powers:**
$$
A^k = V\Lambda^k V^{-1}
$$

### 4.5 Spectral Theorem

For symmetric $A$:
$$
A = Q\Lambda Q^T
$$

where $Q$ is orthogonal and $\Lambda$ is diagonal with real eigenvalues.

---

## 5. Singular Value Decomposition (SVD)

### 5.1 Full SVD

For any $m \times n$ matrix $A$:
$$
A = U\Sigma V^T
$$

where:
- $U$ is $m \times m$ orthogonal (left singular vectors)
- $\Sigma$ is $m \times n$ diagonal (singular values)
- $V$ is $n \times n$ orthogonal (right singular vectors)

### 5.2 Reduced SVD

$$
A = U_r \Sigma_r V_r^T
$$

where $r = \text{rank}(A)$

### 5.3 Properties

Singular values: $\sigma_i = \sqrt{\lambda_i(A^T A)}$

**Low-rank approximation (Eckart-Young):**
$$
A_k = \sum_{i=1}^{k} \sigma_i \mathbf{u}_i \mathbf{v}_i^T
$$

minimizes $||A - B||_F$ over all rank-$k$ matrices $B$.

### 5.4 Pseudoinverse

$$
A^+ = V\Sigma^+ U^T
$$

where $\Sigma^+$ has $1/\sigma_i$ on diagonal for nonzero $\sigma_i$

---

## 6. Matrix Calculus

### 6.1 Scalar by Vector

$$
\frac{\partial}{\partial \mathbf{x}}(\mathbf{a}^T\mathbf{x}) = \mathbf{a}
$$

$$
\frac{\partial}{\partial \mathbf{x}}(\mathbf{x}^T A\mathbf{x}) = (A + A^T)\mathbf{x}
$$

For symmetric $A$:
$$
\frac{\partial}{\partial \mathbf{x}}(\mathbf{x}^T A\mathbf{x}) = 2A\mathbf{x}
$$

### 6.2 Vector by Vector

$$
\frac{\partial}{\partial \mathbf{x}}(A\mathbf{x}) = A
$$

$$
\frac{\partial}{\partial \mathbf{x}}(\mathbf{x}^T A) = A^T
$$

### 6.3 Scalar by Matrix

$$
\frac{\partial}{\partial A}\text{tr}(AB) = B^T
$$

$$
\frac{\partial}{\partial A}\text{tr}(ABA^T) = A(B + B^T)
$$

$$
\frac{\partial}{\partial A}\log\det(A) = A^{-T}
$$

---

## 7. QR Decomposition

$$
A = QR
$$

where $Q$ is orthogonal and $R$ is upper triangular.

**Gram-Schmidt process:**

\begin{align}
\mathbf{u}_1 &= \mathbf{a}_1 \\
\mathbf{u}_k &= \mathbf{a}_k - \sum_{j=1}^{k-1} \text{proj}_{\mathbf{u}_j}\mathbf{a}_k \\
\mathbf{q}_k &= \frac{\mathbf{u}_k}{||\mathbf{u}_k||}
\end{align}

---

## 8. Least Squares

### 8.1 Normal Equations

For $A\mathbf{x} = \mathbf{b}$ (overdetermined):
$$
A^T A \mathbf{x} = A^T \mathbf{b}
$$

$$
\hat{\mathbf{x}} = (A^T A)^{-1} A^T \mathbf{b}
$$

### 8.2 Via SVD

$$
\hat{\mathbf{x}} = A^+ \mathbf{b} = V\Sigma^+ U^T \mathbf{b}
$$

### 8.3 Regularized (Ridge Regression)

$$
\hat{\mathbf{x}} = (A^T A + \lambda I)^{-1} A^T \mathbf{b}
$$
