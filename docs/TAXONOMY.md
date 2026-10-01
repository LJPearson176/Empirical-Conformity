# Taxonomy of Conformity in Human-LLM Cybernetic Systems

This taxonomy formalizes the empirical and theoretical strata of conformity that arise when humans interact with world-scale Large Language Models (LLMs). It serves as the classification framework for the research catalog in `corpus/`.

---

## 1. Multi-Level Classification Framework

| Level | Dimension | Primary Observable Phenomenon | Core Empirical Metric |
| :--- | :--- | :--- | :--- |
| **L1** | **Lexical Conformity** | Word-choice entrenchment, sudden emergence of LLM signature vocabulary in spontaneous human production. | Excess Word Frequency ($Z$-score), Token Distribution Shift ($\Delta P(w)$). |
| **L2** | **Syntactic & Stylistic Conformity** | Compression of rhetorical variance, homogenization of sentence structures, cadence flattening. | Variance in Reading Complexity ($\sigma^2$), Parse Tree Depth Dispersion, Stylistic Entropy. |
| **L3** | **Semantic & Ideational Conformity** | Ideational narrowing, consensus anchoring, opinion steering toward model preference centroid. | Embedding Space Dispersion, Semantic Entropy, Pre/Post Survey Opinion Drift ($\Delta \theta$). |
| **L4** | **Symbolic & Pragmatic Conformity** | Alteration of communicative intent, adoption of prompt-like instrumental structures, semiotic grounding shifts. | Language Style Matching (LSM), Dialogue Turn Complexity, Accommodation Ratio. |
| **L5** | **Systemic & Second-Order Reflexive Loops** | Autophagous data cycles, model collapse, cultural monoculture, emergence of recursive eigenforms. | Tail Probability Loss ($\mathcal{D}_{KL}$ divergence across generations), Web Corpus Contamination Rate. |

---

## 2. Quantitative Metrics and Formalisms

### 2.1 Level 1: Lexical Conformity Metrics

#### Excess Word Frequency ($Z$-score)
Measures the anomalous elevation of a word $w$ in human corpus $C_t$ post-LLM release ($t > t_0$) compared to an empirical historical baseline ($t \le t_0$):

$$Z(w) = \frac{f_t(w) - \mu_{\text{pre}}(w)}{\sigma_{\text{pre}}(w)}$$

Where:
- $f_t(w)$ is the relative frequency of word $w$ at time $t$.
- $\mu_{\text{pre}}(w)$ and $\sigma_{\text{pre}}(w)$ are the historical mean and standard deviation.
- Words with $Z(w) > 4.0$ that correlate with LLM release dates (e.g. November 2022) are classified as *excess marker tokens* (e.g. *delve*, *showcase*, *pivotal*, *intricacies*, *meticulous*).

#### Active Vocabulary Entrenchment ($\mathcal{E}$)
Quantifies the cross-modal persistence of LLM vocabulary in forced-choice or spontaneous spoken tasks following a conversational exposure:

$$\mathcal{E}(w) = P(w \in \text{SpokenOutput} \mid \text{LLM Exposure}) - P(w \in \text{SpokenOutput} \mid \text{Control})$$

As shown by Brinkmann et al. (2024), $\mathcal{E}(w)$ remains significantly positive even after cognitive distractor tasks.

---

### 2.2 Level 2: Syntactic & Stylistic Conformity Metrics

#### Variance in Textual Complexity ($\Delta \text{Var}$)
Quantifies the contraction in stylistic diversity across a population of writers after adopting AI assistance:

$$\Delta \text{Var} = 1 - \frac{\text{Var}(\text{Complexity}_{\text{assisted}})}{\text{Var}(\text{Complexity}_{\text{unassisted}})}$$

Empirical studies on student and professional writing demonstrate that $\Delta \text{Var}$ typically falls between $0.21$ and $0.50$ (a 21% to 50% collapse in structural diversity), even while individual readability scores improve.

#### Stylistic Entropy ($H_{\text{style}}$)
Measures the diversity of syntactic constructions (e.g., distribution of part-of-speech $n$-grams):

$$H_{\text{style}} = -\sum_{i} p(g_i) \log_2 p(g_i)$$

A sharp decline in $H_{\text{style}}$ indicates rhetorical monoculture.

---

### 2.3 Level 3: Semantic & Ideational Conformity Metrics

#### Embedding Dispersion / Semantic Volume ($V_{\text{semantic}}$)
Measures the spatial volume occupied by human responses in a semantic embedding space:

$$V_{\text{semantic}} = \det(\text{Cov}(\mathbf{e}_1, \mathbf{e}_2, \dots, \mathbf{e}_N))$$

Where $\mathbf{e}_i \in \mathbb{R}^d$ is the dense sentence embedding of text $i$. Under semantic conformity, $V_{\text{semantic}} \to 0$, indicating that ideas cluster tightly around the model's centroid.

#### Latent Opinion Drift ($\Delta \theta$)
Quantifies ideological or opinion convergence following co-writing or chat interaction:

$$\Delta \theta = \|\theta_{\text{post}} - \theta_{\text{model}}\| - \|\theta_{\text{pre}} - \theta_{\text{model}}\|$$

A negative value indicates that human beliefs have drifted toward the machine's latent stance.

---

### 2.4 Level 4: Symbolic & Pragmatic Metrics

#### Language Style Matching (LSM)
Evaluates the degree to which a human speaker unconsciously mirrors the function word frequencies of the LLM:

$$\text{LSM} = 1 - \frac{1}{9}\sum_{c=1}^{9} \frac{|f_{\text{human}}(c) - f_{\text{LLM}}(c)|}{f_{\text{human}}(c) + f_{\text{LLM}}(c) + 0.0001}$$

Over the 9 standard LIWC function word categories (pronouns, prepositions, articles, conjunctions, auxiliary verbs, adverbs, negations, quantifiers, relative words).

---

### 2.5 Level 5: Systemic & Second-Order Metrics

#### Model Collapse / Tail Information Loss ($\mathcal{D}_{KL}$)
In a recursive data generation regime where model generation $M_{k+1}$ trains on the output distribution of $M_k$:

$$\mathcal{D}_{KL}(P_0 \parallel P_k) = \sum_{x \in \mathcal{X}} P_0(x) \log \frac{P_0(x)}{P_k(x)}$$

As $k$ grows, low-probability tail phenomena are permanently extinguished, leaving only the modal eigenform.

---

## 3. Observational Substrates

1. **Spoken Corpora**: Unscripted conversational podcasts (e.g. Spotify/Apple podcasts transcripts), broadcast interviews, oral histories.
2. **Scientific Literature**: PubMed abstracts, arXiv preprints, bioRxiv preprints, OpenAlex metadata.
3. **Peer Review Corpora**: OpenReview conference reviews (NeurIPS, ICLR, ICML), grant review archives.
4. **Pedagogical & Student Writing**: High school and university essay corpora before and after November 2022.
5. **Collaborative Code Corpora**: GitHub commits, pull request discussions, StackOverflow solutions.
