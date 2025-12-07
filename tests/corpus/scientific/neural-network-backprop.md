# Neural Network Backpropagation: A Mathematical Treatment

## Abstract

This document provides a rigorous mathematical derivation of the backpropagation algorithm for training feedforward neural networks. We cover the chain rule application, gradient computation, and common activation functions.

## 1. Introduction

Neural networks learn by adjusting weights to minimize a loss function. The backpropagation algorithm efficiently computes gradients of the loss with respect to each weight using the chain rule of calculus.

Consider a network with $L$ layers, where layer $l$ has weights $W^{(l)}$ and biases $b^{(l)}$.

## 2. Forward Propagation

### 2.1 Layer Computations

For each layer $l = 1, \ldots, L$:

**Pre-activation:**
$$
z^{(l)} = W^{(l)} a^{(l-1)} + b^{(l)}
$$

**Activation:**
$$
a^{(l)} = \sigma(z^{(l)})
$$

where $a^{(0)} = x$ (input) and $\sigma$ is the activation function.

### 2.2 Activation Functions

**Sigmoid:**
$$
\sigma(z) = \frac{1}{1 + e^{-z}}, \quad \sigma'(z) = \sigma(z)(1 - \sigma(z))
$$

**Tanh:**
$$
\tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}}, \quad \tanh'(z) = 1 - \tanh^2(z)
$$

**ReLU:**
$$
\text{ReLU}(z) = \max(0, z), \quad \text{ReLU}'(z) = \begin{cases} 1 & z > 0 \\ 0 & z \leq 0 \end{cases}
$$

**Leaky ReLU:**
$$
\text{LeakyReLU}(z) = \begin{cases} z & z > 0 \\ \alpha z & z \leq 0 \end{cases}
$$

**Softmax** (for output layer):
$$
\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}
$$

**GELU:**
$$
\text{GELU}(x) = x \cdot \Phi(x) = x \cdot \frac{1}{2}\left[1 + \text{erf}\left(\frac{x}{\sqrt{2}}\right)\right]
$$

## 3. Loss Functions

### 3.1 Mean Squared Error

For regression:
$$
\mathcal{L}_{MSE} = \frac{1}{2N}\sum_{i=1}^{N}||y_i - \hat{y}_i||^2
$$

Gradient with respect to output:
$$
\frac{\partial \mathcal{L}_{MSE}}{\partial \hat{y}} = \hat{y} - y
$$

### 3.2 Cross-Entropy Loss

For classification with softmax output:
$$
\mathcal{L}_{CE} = -\sum_{c=1}^{C} y_c \log(\hat{y}_c)
$$

Combined gradient (cross-entropy + softmax):
$$
\frac{\partial \mathcal{L}_{CE}}{\partial z_i} = \hat{y}_i - y_i
$$

## 4. Backpropagation Algorithm

### 4.1 Output Layer Error

Define the error signal at layer $l$:
$$
\delta^{(l)} = \frac{\partial \mathcal{L}}{\partial z^{(l)}}
$$

For the output layer $L$:
$$
\delta^{(L)} = \frac{\partial \mathcal{L}}{\partial a^{(L)}} \odot \sigma'(z^{(L)})
$$

### 4.2 Hidden Layer Errors

For layers $l = L-1, \ldots, 1$:
$$
\delta^{(l)} = (W^{(l+1)})^T \delta^{(l+1)} \odot \sigma'(z^{(l)})
$$

### 4.3 Gradient Computation

**Weight gradients:**
$$
\frac{\partial \mathcal{L}}{\partial W^{(l)}} = \delta^{(l)} (a^{(l-1)})^T
$$

**Bias gradients:**
$$
\frac{\partial \mathcal{L}}{\partial b^{(l)}} = \delta^{(l)}
$$

### 4.4 Batch Gradient

For a mini-batch of $m$ samples:
$$
\frac{\partial \mathcal{L}}{\partial W^{(l)}} = \frac{1}{m}\sum_{i=1}^{m} \delta_i^{(l)} (a_i^{(l-1)})^T
$$

## 5. Optimization

### 5.1 Stochastic Gradient Descent

$$
W_{t+1} = W_t - \eta \nabla_W \mathcal{L}
$$

### 5.2 Momentum

$$
v_{t+1} = \gamma v_t + \eta \nabla_W \mathcal{L}
$$

$$
W_{t+1} = W_t - v_{t+1}
$$

### 5.3 Adam Optimizer

\begin{align}
m_t &= \beta_1 m_{t-1} + (1 - \beta_1) g_t \\
v_t &= \beta_2 v_{t-1} + (1 - \beta_2) g_t^2 \\
\hat{m}_t &= \frac{m_t}{1 - \beta_1^t} \\
\hat{v}_t &= \frac{v_t}{1 - \beta_2^t} \\
W_{t+1} &= W_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t
\end{align}

Default hyperparameters: $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$

## 6. Regularization

### 6.1 L2 Regularization (Weight Decay)

$$
\mathcal{L}_{reg} = \mathcal{L} + \frac{\lambda}{2}\sum_l ||W^{(l)}||_F^2
$$

Gradient modification:
$$
\nabla_{W^{(l)}} \mathcal{L}_{reg} = \nabla_{W^{(l)}} \mathcal{L} + \lambda W^{(l)}
$$

### 6.2 Dropout

During training, randomly set activations to zero:
$$
\tilde{a}^{(l)} = \frac{1}{1-p} \cdot a^{(l)} \odot m^{(l)}
$$

where $m^{(l)} \sim \text{Bernoulli}(1-p)$ and $p$ is dropout rate.

### 6.3 Batch Normalization

For mini-batch $\mathcal{B} = \{x_1, \ldots, x_m\}$:

\begin{align}
\mu_\mathcal{B} &= \frac{1}{m}\sum_{i=1}^{m} x_i \\
\sigma_\mathcal{B}^2 &= \frac{1}{m}\sum_{i=1}^{m}(x_i - \mu_\mathcal{B})^2 \\
\hat{x}_i &= \frac{x_i - \mu_\mathcal{B}}{\sqrt{\sigma_\mathcal{B}^2 + \epsilon}} \\
y_i &= \gamma \hat{x}_i + \beta
\end{align}

## 7. Weight Initialization

### 7.1 Xavier/Glorot Initialization

For layer with $n_{in}$ inputs and $n_{out}$ outputs:
$$
W \sim \mathcal{U}\left(-\sqrt{\frac{6}{n_{in} + n_{out}}}, \sqrt{\frac{6}{n_{in} + n_{out}}}\right)
$$

or with normal distribution:
$$
W \sim \mathcal{N}\left(0, \frac{2}{n_{in} + n_{out}}\right)
$$

### 7.2 He Initialization

For ReLU networks:
$$
W \sim \mathcal{N}\left(0, \frac{2}{n_{in}}\right)
$$

## 8. Convolutional Layers

### 8.1 Convolution Operation

For input $X$ and kernel $K$:
$$
(X * K)_{ij} = \sum_{m}\sum_{n} X_{i+m, j+n} K_{m,n}
$$

### 8.2 Output Size

For input size $W$, kernel size $K$, padding $P$, and stride $S$:
$$
W_{out} = \left\lfloor \frac{W - K + 2P}{S} \right\rfloor + 1
$$

### 8.3 Backpropagation Through Convolution

Gradient with respect to input:
$$
\frac{\partial \mathcal{L}}{\partial X} = \frac{\partial \mathcal{L}}{\partial Y} * K^{rot180}
$$

Gradient with respect to kernel:
$$
\frac{\partial \mathcal{L}}{\partial K} = X * \frac{\partial \mathcal{L}}{\partial Y}
$$

## 9. Recurrent Layers

### 9.1 Simple RNN

$$
h_t = \tanh(W_{hh} h_{t-1} + W_{xh} x_t + b_h)
$$

$$
y_t = W_{hy} h_t + b_y
$$

### 9.2 LSTM

\begin{align}
f_t &= \sigma(W_f \cdot [h_{t-1}, x_t] + b_f) \quad \text{(forget gate)} \\
i_t &= \sigma(W_i \cdot [h_{t-1}, x_t] + b_i) \quad \text{(input gate)} \\
\tilde{C}_t &= \tanh(W_C \cdot [h_{t-1}, x_t] + b_C) \quad \text{(candidate)} \\
C_t &= f_t \odot C_{t-1} + i_t \odot \tilde{C}_t \quad \text{(cell state)} \\
o_t &= \sigma(W_o \cdot [h_{t-1}, x_t] + b_o) \quad \text{(output gate)} \\
h_t &= o_t \odot \tanh(C_t) \quad \text{(hidden state)}
\end{align}

### 9.3 GRU

\begin{align}
z_t &= \sigma(W_z \cdot [h_{t-1}, x_t]) \quad \text{(update gate)} \\
r_t &= \sigma(W_r \cdot [h_{t-1}, x_t]) \quad \text{(reset gate)} \\
\tilde{h}_t &= \tanh(W \cdot [r_t \odot h_{t-1}, x_t]) \\
h_t &= (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t
\end{align}

## 10. Attention Mechanism

### 10.1 Scaled Dot-Product Attention

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

### 10.2 Multi-Head Attention

$$
\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W^O
$$

where:
$$
\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)
$$

## Conclusion

Backpropagation enables efficient gradient computation in neural networks by applying the chain rule systematically from output to input layers. Combined with optimization algorithms like Adam and regularization techniques, it forms the foundation of modern deep learning.
