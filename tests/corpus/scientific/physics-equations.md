# Physics Equations Reference

Fundamental equations from classical mechanics, electromagnetism, thermodynamics, and quantum mechanics.

## 1. Classical Mechanics

### 1.1 Newton's Laws

**First Law:** A body remains at rest or in uniform motion unless acted upon by a force.

**Second Law:**
$$
\mathbf{F} = m\mathbf{a} = m\frac{d\mathbf{v}}{dt} = \frac{d\mathbf{p}}{dt}
$$

**Third Law:** For every action, there is an equal and opposite reaction.
$$
\mathbf{F}_{12} = -\mathbf{F}_{21}
$$

### 1.2 Kinematics

**Constant acceleration:**
$$
v = v_0 + at
$$

$$
x = x_0 + v_0 t + \frac{1}{2}at^2
$$

$$
v^2 = v_0^2 + 2a(x - x_0)
$$

### 1.3 Work and Energy

**Work done by a force:**
$$
W = \int_C \mathbf{F} \cdot d\mathbf{r}
$$

**Kinetic energy:**
$$
K = \frac{1}{2}mv^2
$$

**Potential energy (gravity):**
$$
U = mgh
$$

**Work-energy theorem:**
$$
W_{net} = \Delta K = K_f - K_i
$$

### 1.4 Conservation Laws

**Conservation of momentum:**
$$
\sum_i m_i \mathbf{v}_i = \text{constant}
$$

**Conservation of energy:**
$$
E = K + U = \text{constant}
$$

**Conservation of angular momentum:**
$$
\mathbf{L} = \mathbf{r} \times \mathbf{p} = I\boldsymbol{\omega}
$$

### 1.5 Lagrangian Mechanics

**Lagrangian:**
$$
\mathcal{L} = T - V
$$

**Euler-Lagrange equation:**
$$
\frac{d}{dt}\frac{\partial \mathcal{L}}{\partial \dot{q}_i} - \frac{\partial \mathcal{L}}{\partial q_i} = 0
$$

### 1.6 Hamiltonian Mechanics

**Hamiltonian:**
$$
\mathcal{H} = \sum_i p_i \dot{q}_i - \mathcal{L} = T + V
$$

**Hamilton's equations:**
$$
\dot{q}_i = \frac{\partial \mathcal{H}}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial \mathcal{H}}{\partial q_i}
$$

---

## 2. Electromagnetism

### 2.1 Maxwell's Equations

**In differential form:**

\begin{align}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \quad \text{(Gauss's law)} \\
\nabla \cdot \mathbf{B} &= 0 \quad \text{(No magnetic monopoles)} \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \quad \text{(Faraday's law)} \\
\nabla \times \mathbf{B} &= \mu_0\mathbf{J} + \mu_0\varepsilon_0\frac{\partial \mathbf{E}}{\partial t} \quad \text{(Ampère-Maxwell)}
\end{align}

**In integral form:**

$$
\oint_S \mathbf{E} \cdot d\mathbf{A} = \frac{Q_{enc}}{\varepsilon_0}
$$

$$
\oint_S \mathbf{B} \cdot d\mathbf{A} = 0
$$

$$
\oint_C \mathbf{E} \cdot d\mathbf{l} = -\frac{d\Phi_B}{dt}
$$

$$
\oint_C \mathbf{B} \cdot d\mathbf{l} = \mu_0 I_{enc} + \mu_0\varepsilon_0\frac{d\Phi_E}{dt}
$$

### 2.2 Electromagnetic Potentials

**Electric potential:**
$$
\mathbf{E} = -\nabla\phi - \frac{\partial \mathbf{A}}{\partial t}
$$

**Magnetic potential:**
$$
\mathbf{B} = \nabla \times \mathbf{A}
$$

### 2.3 Coulomb's Law

$$
\mathbf{F} = \frac{1}{4\pi\varepsilon_0}\frac{q_1 q_2}{r^2}\hat{\mathbf{r}}
$$

### 2.4 Lorentz Force

$$
\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})
$$

### 2.5 Electromagnetic Waves

**Wave equation:**
$$
\nabla^2 \mathbf{E} = \mu_0\varepsilon_0\frac{\partial^2 \mathbf{E}}{\partial t^2}
$$

**Speed of light:**
$$
c = \frac{1}{\sqrt{\mu_0\varepsilon_0}} \approx 3 \times 10^8 \text{ m/s}
$$

**Poynting vector:**
$$
\mathbf{S} = \frac{1}{\mu_0}\mathbf{E} \times \mathbf{B}
$$

---

## 3. Thermodynamics

### 3.1 Laws of Thermodynamics

**First Law:**
$$
dU = \delta Q - \delta W
$$

**Second Law (entropy):**
$$
dS \geq \frac{\delta Q}{T}
$$

**Third Law:** As $T \to 0$, $S \to S_0$ (constant)

### 3.2 Ideal Gas Law

$$
PV = nRT = Nk_BT
$$

**Internal energy:**
$$
U = \frac{f}{2}nRT
$$

where $f$ is degrees of freedom.

### 3.3 Heat Capacity

**At constant volume:**
$$
C_V = \left(\frac{\partial U}{\partial T}\right)_V
$$

**At constant pressure:**
$$
C_P = \left(\frac{\partial H}{\partial T}\right)_P
$$

**Relation:**
$$
C_P - C_V = nR
$$

### 3.4 Thermodynamic Potentials

**Enthalpy:**
$$
H = U + PV
$$

**Helmholtz free energy:**
$$
F = U - TS
$$

**Gibbs free energy:**
$$
G = H - TS = U + PV - TS
$$

### 3.5 Statistical Mechanics

**Boltzmann distribution:**
$$
P_i = \frac{e^{-E_i/k_BT}}{Z}
$$

**Partition function:**
$$
Z = \sum_i e^{-E_i/k_BT}
$$

**Entropy:**
$$
S = k_B \ln \Omega
$$

---

## 4. Quantum Mechanics

### 4.1 Schrödinger Equation

**Time-dependent:**
$$
i\hbar\frac{\partial}{\partial t}\Psi(\mathbf{r}, t) = \hat{H}\Psi(\mathbf{r}, t)
$$

**Time-independent:**
$$
\hat{H}\psi(\mathbf{r}) = E\psi(\mathbf{r})
$$

**Hamiltonian operator:**
$$
\hat{H} = -\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r})
$$

### 4.2 Uncertainty Principle

$$
\Delta x \Delta p \geq \frac{\hbar}{2}
$$

$$
\Delta E \Delta t \geq \frac{\hbar}{2}
$$

### 4.3 Wave Function Properties

**Normalization:**
$$
\int_{-\infty}^{\infty} |\Psi(x, t)|^2 dx = 1
$$

**Expectation value:**
$$
\langle A \rangle = \int \Psi^* \hat{A} \Psi \, dx
$$

### 4.4 Quantum Harmonic Oscillator

**Energy levels:**
$$
E_n = \hbar\omega\left(n + \frac{1}{2}\right), \quad n = 0, 1, 2, \ldots
$$

### 4.5 Hydrogen Atom

**Energy levels:**
$$
E_n = -\frac{13.6 \text{ eV}}{n^2} = -\frac{m_e e^4}{32\pi^2\varepsilon_0^2\hbar^2 n^2}
$$

**Bohr radius:**
$$
a_0 = \frac{4\pi\varepsilon_0\hbar^2}{m_e e^2} \approx 0.529 \text{ Å}
$$

### 4.6 Angular Momentum

**Commutation relations:**
$$
[L_x, L_y] = i\hbar L_z
$$

**Eigenvalues:**
$$
L^2|l, m\rangle = \hbar^2 l(l+1)|l, m\rangle
$$

$$
L_z|l, m\rangle = \hbar m|l, m\rangle
$$

---

## 5. Special Relativity

### 5.1 Lorentz Transformations

$$
x' = \gamma(x - vt)
$$

$$
t' = \gamma\left(t - \frac{vx}{c^2}\right)
$$

where $\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}$

### 5.2 Time Dilation

$$
\Delta t = \gamma \Delta t_0
$$

### 5.3 Length Contraction

$$
L = \frac{L_0}{\gamma}
$$

### 5.4 Energy-Momentum Relation

$$
E^2 = (pc)^2 + (m_0 c^2)^2
$$

**Relativistic energy:**
$$
E = \gamma m_0 c^2
$$

**Rest energy:**
$$
E_0 = m_0 c^2
$$

### 5.5 Four-Momentum

$$
p^\mu = (E/c, \mathbf{p})
$$

**Invariant:**
$$
p^\mu p_\mu = -m_0^2 c^2
$$

---

## 6. Fundamental Constants

| Constant | Symbol | Value |
|----------|--------|-------|
| Speed of light | $c$ | $2.998 \times 10^8$ m/s |
| Planck constant | $h$ | $6.626 \times 10^{-34}$ J·s |
| Reduced Planck | $\hbar$ | $1.055 \times 10^{-34}$ J·s |
| Boltzmann constant | $k_B$ | $1.381 \times 10^{-23}$ J/K |
| Electron charge | $e$ | $1.602 \times 10^{-19}$ C |
| Vacuum permittivity | $\varepsilon_0$ | $8.854 \times 10^{-12}$ F/m |
| Vacuum permeability | $\mu_0$ | $4\pi \times 10^{-7}$ H/m |
| Gravitational constant | $G$ | $6.674 \times 10^{-11}$ N·m²/kg² |
