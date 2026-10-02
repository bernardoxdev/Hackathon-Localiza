# RUPTURA 2026 --- Case 2: Do atendimento ao hábito

## Dossiê de diagnóstico, pesquisa, ideias e oportunidades para o app Localiza Assinatura

> **Objetivo deste documento:** consolidar, em um único material de
> trabalho, tudo o que foi extraído do Case 2 do RUPTURA 2026,
> informações atuais encontradas no site e nas lojas oficiais do
> aplicativo Localiza Assinatura, hipóteses de produto, ideias de
> solução, oportunidades de IA, jornadas, métricas, riscos, arquitetura
> e possibilidades de prototipação.
>
> **Importante:** este documento diferencia: - **DADO DO CASE** ---
> informação fornecida pela organização no material do desafio; - **DADO
> ATUAL DO PRODUTO** --- informação encontrada nas páginas oficiais da
> Localiza/lojas de aplicativos; - **INFERÊNCIA** --- interpretação
> feita a partir dos dados; - **HIPÓTESE** --- algo que ainda precisa
> ser validado; - **PROPOSTA** --- ideia criada para o hackathon.

------------------------------------------------------------------------

# 1. Resumo executivo

## O desafio

O Case 2 do RUPTURA 2026 é:

> **"Do atendimento ao hábito"**

Pergunta do desafio:

> **Como transformar o app do Localiza Assinatura em um companheiro de
> mobilidade, e não apenas um canal de atendimento?**

O problema apresentado pela Localiza não é simplesmente "o app tem
poucos acessos". O próprio material orienta que a equipe não deve buscar
aumento de acessos sem valor.

O objetivo é:

> **Ampliar a relevância do app na rotina dos clientes através de
> funcionalidades que gerem valor adicional na jornada de mobilidade,
> fortalecendo a relação com a marca e gerando impacto para usuário e
> negócio.**

## A tese central para o grupo

O app já resolve várias necessidades importantes.

O problema é que a relação atual tende a ser:

**necessidade → abre app → resolve → fecha app**

A oportunidade é transformar isso em:

**rotina → contexto → antecipação → ajuda → valor → hábito**

A pergunta mais importante para a solução não deveria ser:

> "Como fazemos o cliente abrir mais o app?"

E sim:

> **"Que problema real da mobilidade conseguimos resolver melhor porque
> somos a Localiza Assinatura?"**

------------------------------------------------------------------------

# 2. Fontes utilizadas

## Fontes primárias do hackathon

1.  **Manual do Participante RUPTURA 2026**
2.  **Apresentação dos Cases Localiza / Localiza Assinatura**
3.  Dados quantitativos apresentados nos slides do Case 2.

## Pesquisa externa atual

Também foram consultadas fontes oficiais da Localiza e das lojas
oficiais:

-   Site oficial Localiza Assinatura
-   Página oficial do aplicativo no Google Play
-   Página oficial do aplicativo na App Store
-   Páginas oficiais do Clube de Benefícios
-   Conteúdos oficiais sobre funcionamento da assinatura

### Fontes externas

-   Localiza Assinatura: https://assinatura.localiza.com/
-   App Android:
    https://play.google.com/store/apps/details?id=com.localiza.meoo.app
-   App iOS:
    https://apps.apple.com/br/app/localiza-assinatura-meoo/id1528537131
-   Clube de Benefícios:
    https://assinatura.localiza.com/clube-de-beneficios/
-   Carros por assinatura: https://assinatura.localiza.com/assinatura
-   Blog oficial: https://assinatura.localiza.com/blog/

------------------------------------------------------------------------

# 3. O que o Case 2 realmente apresenta

## 3.1 Contexto

O material do Case informa que:

-   o cliente de assinatura possui um aplicativo exclusivo;
-   o app é utilizado principalmente para resolver necessidades
    pontuais;
-   exemplos incluem agendamento de serviços, busca de informações e
    pagamentos;
-   a rotina de mobilidade acontece continuamente;
-   dirigir, abastecer, estacionar e cuidar do carro são atividades
    recorrentes;
-   veículos estão cada vez mais conectados;
-   novas montadoras têm se destacado por oferecer aplicativos com
    funcionalidades adicionais;
-   existe oportunidade para o app ser parte da rotina e não apenas um
    canal de resolução de problemas.

### Interpretação

A Localiza já possui um **canal digital funcional e relevante**.

O desafio é transformar esse canal em uma **camada de relacionamento e
utilidade cotidiana**.

------------------------------------------------------------------------

# 4. Dados quantitativos do Case 2

## 4.1 Base de clientes

O material informa:

-   aproximadamente **70 mil clientes**;
-   mais de **80%** acessam o aplicativo mensalmente;
-   aproximadamente **53 mil MAU**;
-   aproximadamente **31 mil WAU**.

## 4.2 Distribuição de acessos

Entre os usuários:

-   **36%** acessam 1--2 vezes por mês;
-   **28%** acessam 3--5 vezes;
-   **19%** acessam 6--10 vezes;
-   **11%** acessam 11--20 vezes;
-   **6%** acessam 21+ vezes.

O próprio material resume isso indicando que:

-   existe alta adesão mensal;
-   mas existe uma concentração relevante de usuários com poucos
    acessos;
-   uma parcela menor apresenta alto engajamento.

## 4.3 NPS

O case informa:

-   **App NPS = 84**
-   NPS relacional da assinatura ≈ **45**

Isso é extremamente importante.

O problema não parece ser simplesmente:

> "o aplicativo é ruim."

Pelo contrário.

A oportunidade é:

> **o cliente gosta do app quando precisa dele, mas essa percepção
> positiva não está necessariamente se convertendo em relacionamento
> contínuo com a marca.**

------------------------------------------------------------------------

# 5. Dores apresentadas no Case

## 5.1 Dores do cliente

Segundo o material:

### 1. Pouco valor fora das necessidades contratuais

O cliente encontra valor quando precisa:

-   resolver alguma questão;
-   consultar informações;
-   fazer pagamentos;
-   agendar manutenção;
-   consultar dados.

Fora desses momentos, existem poucos motivos para retornar.

### 2. Benefícios pouco conectados ao contexto

Benefícios e serviços existentes nem sempre estão relacionados ao
momento específico ou à necessidade do cliente.

### 3. Poucas experiências exclusivas

Existe espaço para criar utilidades que o cliente encontre
especificamente dentro do ecossistema Localiza Assinatura.

### 4. Falta de motivos recorrentes

A rotina do motorista é frequente.

O aplicativo não necessariamente acompanha essa frequência.

------------------------------------------------------------------------

# 6. Dores da Localiza

## 6.1 Engajamento digital

O uso pouco frequente fora de necessidades específicas reduz
oportunidades de relacionamento.

## 6.2 Percepção de valor

O cliente pode valorizar o app, mas não necessariamente perceber todo o
valor da assinatura através dele.

## 6.3 Atendimento

O Case informa:

-   mais de **80 mil contatos mensais**;
-   aproximadamente **75% via chat**;
-   aproximadamente **25% via telefone**.

Existe oportunidade de resolver digitalmente necessidades que não exigem
atendimento humano.

## 6.4 Renovação

O Case informa:

-   aproximadamente **48% dos clientes renovam** ao final do contrato.

## 6.5 Indicação

O Case informa:

-   aproximadamente **7% dos clientes indicam amigo ou familiar**.

Esses dados não significam automaticamente que "baixo uso do app causa
baixa renovação". Isso seria uma inferência não comprovada pelo
material.

A formulação correta é:

> **Existe uma oportunidade de usar o relacionamento digital para
> fortalecer a percepção de valor e a conexão com a marca.**

------------------------------------------------------------------------

# 7. Jornada atual apresentada

A jornada do Case é:

``` text
1. Precisa resolver algo
          ↓
2. Acessa o app
          ↓
3. Resolve pontualmente
          ↓
4. Fecha o aplicativo
          ↓
5. Só retorna com uma nova necessidade
```

A característica principal é:

> **relação reativa e pontual.**

------------------------------------------------------------------------

# 8. Jornada que queremos construir

A oportunidade pode ser representada assim:

``` text
ROTINA
  ↓
CONTEXTO
  ↓
NECESSIDADE
  ↓
APP ANTECIPA
  ↓
AÇÃO
  ↓
VALOR
  ↓
CONFIANÇA
  ↓
HÁBITO
```

O app deixa de ser:

> "onde resolvo algo"

e passa a ser:

> **"onde a Localiza me ajuda a fazer minha mobilidade funcionar
> melhor."**

------------------------------------------------------------------------

# 9. O que o aplicativo oferece hoje

Com base no material do Case e na descrição atual das lojas oficiais, o
aplicativo oferece ou se relaciona com:

## Conta e assinatura

-   acompanhamento do pedido;
-   informações da assinatura;
-   resumo do contrato;
-   documentos;
-   CRLV;
-   informações financeiras.

## Financeiro

-   faturas;
-   valores;
-   vencimentos;
-   histórico;
-   pagamento/cadastro de cartão.

## Quilometragem

-   acompanhamento de quilômetros percorridos;
-   alertas relacionados ao limite contratado.

## Manutenção

-   agendamento de revisão;
-   manutenção preventiva;
-   manutenção corretiva;
-   acompanhamento do serviço.

## Multas

-   consulta de multas;
-   acompanhamento;
-   indicação de condutor.

## Telemetria/localização/alertas

O material do Case apresenta:

-   localização em tempo real;
-   alertas de movimentação;
-   alertas de carro ligado;
-   informações de combustível e bateria.

## Benefícios

-   Clube de Benefícios;
-   descontos;
-   parceiros;
-   experiências;
-   serviços.

## Member Get Member

-   indicação de amigos/familiares;
-   acompanhamento da indicação;
-   benefícios/descontos associados.

## Suporte

-   ajuda;
-   canais de contato;
-   assistência;
-   situações emergenciais;
-   registro de danos.

## Notificações

A página atual do Google Play informa que o aplicativo envia
notificações sobre:

-   novidades;
-   promoções;
-   disponibilidade do carro para retirada;
-   proximidade de revisão.

------------------------------------------------------------------------

# 10. O que mudou/foi confirmado pela pesquisa atual

A pesquisa nas fontes oficiais mostra que a proposta do produto continua
bastante concentrada em:

**controle da assinatura + manutenção + documentos + financeiro +
multas + benefícios + suporte.**

A página atual do Google Play também informa que o app possui mais de
**100 mil downloads** e foi atualizado em **24 de setembro de 2026**.

Isso é relevante para o hackathon porque demonstra que estamos
trabalhando sobre um produto digital existente e ativo, e não sobre um
aplicativo hipotético.

------------------------------------------------------------------------

# 11. A proposta atual da Localiza Assinatura

O site atual posiciona o produto em torno de:

-   carro novo;
-   praticidade;
-   previsibilidade;
-   manutenção;
-   proteção;
-   documentação;
-   IPVA;
-   escolha de modelo;
-   escolha de prazo;
-   escolha de quilometragem;
-   controle pelo aplicativo.

O site também apresenta:

-   mais de 150 modelos;
-   mais de 500 pontos de retirada;
-   mais de 10 mil oficinas parceiras;
-   carro reserva/substituto conforme contratação;
-   assistência 24h;
-   manutenção preventiva e corretiva;
-   troca de pneus;
-   proteção a terceiros;
-   reboque.

Esses elementos são importantes porque mostram que a Localiza já possui
um **ecossistema físico e operacional muito maior que o app**.

------------------------------------------------------------------------

# 12. Insight estratégico

A maior oportunidade pode não ser criar "mais funcionalidades".

Pode ser:

# Transformar o ecossistema Localiza em inteligência contextual dentro do app.

Hoje:

``` text
APP
├── Financeiro
├── KM
├── Manutenção
├── Multas
├── Benefícios
├── Contrato
└── Ajuda
```

Possível evolução:

``` text
                    APP
                     │
             CONTEXTO DO CLIENTE
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
     CARRO         ROTINA       CONTRATO
       │             │             │
       └─────────────┼─────────────┘
                     ↓
             PRÓXIMA NECESSIDADE
                     ↓
               AÇÃO RELEVANTE
```

------------------------------------------------------------------------

# 13. Ideias de solução

A seguir estão as ideias levantadas para o Case 2.

------------------------------------------------------------------------

# IDEIA 1 --- Mobility Home

## Conceito

Transformar a home do app em uma central dinâmica da vida do motorista.

Em vez de apresentar apenas funcionalidades, a home responde:

> **"O que é importante para você agora?"**

## Exemplo

``` text
Bom dia, Bernardo.

Seu carro está pronto para a semana.

● 820 km disponíveis
● Revisão em 1.200 km
● Fatura vence em 6 dias

Para hoje:
→ Veja seus benefícios próximos
→ Planeje sua próxima viagem
→ Agende sua revisão
```

## Problema atacado

Home funcional, porém predominantemente operacional.

## Insight

O usuário não deveria precisar navegar para descobrir o que precisa.

## Tecnologia

-   motor de contexto;
-   regras;
-   personalização.

## IA

Pode selecionar e priorizar conteúdo.

## Dados

-   contrato;
-   KM;
-   manutenção;
-   localização, se disponível;
-   histórico de uso;
-   preferências.

## Risco

Virar apenas um dashboard mais bonito.

## Mitigação

Toda informação exibida precisa gerar uma ação ou valor concreto.

------------------------------------------------------------------------

# IDEIA 2 --- Proactive Care

## Conceito

O app deixa de esperar o cliente perceber um problema.

Ele antecipa necessidades.

## Exemplos

> "Sua revisão está próxima."

> "Você está se aproximando do limite de KM."

> "Seu carro apresenta uma situação que merece atenção."

> "Você tem um benefício relevante próximo da sua localização."

## Problema

A relação atual é reativa.

## Insight

A melhor notificação é aquela que evita que o cliente precise abrir o
app para descobrir um problema.

## IA

Classificar:

-   urgência;
-   relevância;
-   momento;
-   canal.

## Regra fundamental

Não transformar isso em spam.

------------------------------------------------------------------------

# IDEIA 3 --- Mobility Planner

## Conceito

O aplicativo ajuda o cliente a planejar sua mobilidade.

## Exemplo

Cliente informa:

> "Vou viajar sexta-feira para São Paulo."

O app poderia organizar:

-   KM disponível;
-   manutenção;
-   documentação;
-   benefícios;
-   assistência;
-   pontos de parada;
-   informações relevantes.

## HIPÓTESE

Integrações externas poderiam ser necessárias para algumas funções.

Não apresentar integrações inexistentes como se fossem atuais.

------------------------------------------------------------------------

# IDEIA 4 --- Benefícios Contextuais

## Problema

O Clube de Benefícios possui muitos benefícios, mas mostrar uma lista
enorme não significa relevância.

## Solução

O app seleciona:

> **"Benefícios que fazem sentido para você."**

Exemplo:

Cliente em viagem:

-   hotel;
-   estacionamento;
-   aluguel;
-   restaurante;
-   serviços automotivos.

Cliente no cotidiano:

-   estacionamento;
-   serviços;
-   experiências;
-   parceiros locais.

## IA

Recomendação contextual.

## Métrica

-   utilização dos benefícios;
-   conversão de visualização → uso;
-   satisfação.

------------------------------------------------------------------------

# IDEIA 5 --- Subscription Value

## Conceito

Mostrar de forma concreta o valor que o cliente recebe da assinatura.

## Exemplo

``` text
Seu mês com a Localiza

Manutenção
R$ XXX

Assistência
R$ XXX

Documentação
R$ XXX

Benefícios utilizados
R$ XXX

Serviços
R$ XXX

--------------------------------
Valor percebido
R$ XXX
```

## Problema

Grande parte do valor da assinatura é invisível porque o cliente só
percebe quando precisa.

## Insight

> "Valor não percebido é valor que não fortalece relacionamento."

## Cuidado

Não inventar economia.

Os valores precisam vir de dados reais ou ser apresentados como
simulação.

------------------------------------------------------------------------

# IDEIA 6 --- Mobility Missions

## Conceito

Criar pequenas experiências recorrentes.

Exemplo:

> "Confira sua franquia deste mês."

> "Você já está com sua manutenção em dia?"

> "Conheça um benefício que combina com sua rotina."

## Risco

Gamificação artificial.

## Mitigação

Só utilizar quando houver benefício real.

------------------------------------------------------------------------

# IDEIA 7 --- Renewal Companion

## Conceito

Transformar renovação em uma jornada contínua.

Em vez de:

``` text
Contrato acabando
↓
Renovação
```

Criar:

``` text
90 dias
↓
Como está sua experiência?

60 dias
↓
O que mudou na sua rotina?

30 dias
↓
Qual carro faz sentido agora?

Renovação
↓
Nova configuração
```

## Potencial

Muito forte para personalização.

## Risco

Parecer apenas campanha comercial.

## Mitigação

Começar pela necessidade do cliente, não pela venda.

------------------------------------------------------------------------

# IDEIA 8 --- "O que eu preciso hoje?"

## Conceito

Uma camada conversacional dentro do app.

O usuário poderia dizer:

> "Vou viajar amanhã."

> "Meu carro está fazendo um barulho."

> "Preciso fazer a revisão."

> "Quero saber quanto ainda posso rodar."

O sistema identifica a intenção e encaminha para a função correta.

## Importante

Isso não deve ser apresentado como:

> "chatbot de IA".

A tecnologia é apenas uma interface para acessar serviços reais.

------------------------------------------------------------------------

# IDEIA 9 --- Assistente de Mobilidade Contextual

## Conceito

Um assistente que conhece o contexto do contrato e do carro.

Ele poderia combinar:

-   contrato;
-   KM;
-   manutenção;
-   benefícios;
-   localização;
-   histórico;
-   preferências.

## Exemplo

> "Você está planejando uma viagem de 1.200 km. Sua franquia atual é X.
> Sua revisão está próxima. Quer verificar suas opções?"

## Grande potencial

Essa ideia conecta quase todas as anteriores.

------------------------------------------------------------------------

# IDEIA 10 --- "Seu carro, sua rotina"

## Conceito

O app aprende quais são os principais padrões do cliente.

Exemplo:

``` text
Você costuma:

08:00 → trabalho
18:00 → academia
Sexta → viagem
Domingo → família
```

A partir disso, o app oferece valor contextual.

## HIPÓTESE

O nível de personalização possível dependeria dos dados efetivamente
disponíveis e das permissões do usuário.

------------------------------------------------------------------------

# IDEIA 11 --- Localiza Mobility Score

## Conceito

Criar um indicador simples da saúde da jornada do cliente.

Exemplo:

``` text
MOBILITY SCORE

92/100

✓ Manutenção em dia
✓ KM dentro do plano
✓ Documentação regular
✓ Contrato em dia
⚠ Revisão próxima
```

## Risco

Criar uma métrica artificial.

## Mitigação

O score deve representar situações acionáveis, e não apenas gamificação.

------------------------------------------------------------------------

# IDEIA 12 --- "Zero Surpresa"

## Conceito

Uma experiência que identifica antecipadamente tudo que pode gerar
fricção.

``` text
Seu mês sem surpresas

✓ Fatura
✓ KM
✓ Manutenção
✓ Documentos
✓ Multas
✓ Viagem
✓ Assistência
```

## Insight

A promessa da assinatura é previsibilidade.

O app poderia transformar essa promessa em experiência digital.

------------------------------------------------------------------------

# 14. Ideias que podem ser combinadas

Não é necessário escolher uma única funcionalidade.

Uma solução mais robusta pode ser formada por módulos.

## Plataforma conceitual

# Localiza Mobility OS

``` text
                    LOCALIZA
                 MOBILITY OS
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    CONTEXTO        PREVISÃO        AÇÃO
       │              │              │
       ↓              ↓              ↓
     Rotina       Necessidades     Serviços
       │              │              │
       └──────────────┼──────────────┘
                      ↓
                  VALOR
                      ↓
                   HÁBITO
```

Mas existe um risco:

> **"Mobility OS" pode parecer abstrato demais para um pitch de 3
> minutos.**

Uma apresentação melhor pode ter um nome simples e explicar que o
conceito é uma camada de inteligência contextual.

------------------------------------------------------------------------

# 15. Possível solução integrada

## Nome provisório

# Localiza Companion

### Tagline

> **Seu carro. Sua rotina. A Localiza um passo à frente.**

## Conceito

Uma nova camada do app que combina:

1.  contexto;
2.  personalização;
3.  antecipação;
4.  serviços;
5.  benefícios;
6.  relacionamento.

------------------------------------------------------------------------

# 16. Como funcionaria

## Etapa 1 --- Conhecer

O sistema utiliza informações que já fazem parte da jornada do cliente.

## Etapa 2 --- Entender

Identifica:

-   situação;
-   momento;
-   necessidade;
-   prioridade.

## Etapa 3 --- Recomendar

Apresenta uma ação relevante.

## Etapa 4 --- Executar

O cliente resolve dentro do ecossistema Localiza.

## Etapa 5 --- Aprender

O sistema registra a interação para melhorar futuras recomendações,
respeitando privacidade e consentimento.

------------------------------------------------------------------------

# 17. Exemplo de experiência

## Segunda-feira

> "Sua revisão está próxima."

CTA:

**Agendar agora**

------------------------------------------------------------------------

## Quarta-feira

> "Você está dentro da sua franquia de KM."

CTA:

**Ver meu uso**

------------------------------------------------------------------------

## Sexta-feira

> "Vai viajar neste fim de semana?"

CTA:

**Preparar viagem**

------------------------------------------------------------------------

## Domingo

> "Você tem 3 benefícios que podem ser úteis na sua região."

CTA:

**Ver benefícios**

O app deixa de ser uma ferramenta aberta apenas quando há problema.

------------------------------------------------------------------------

# 18. Princípio de produto

## Não queremos aumentar DAU artificialmente.

Queremos aumentar:

> **valor por interação.**

Uma métrica ruim:

> "Número de aberturas."

Uma métrica melhor:

> "Percentual de usuários que resolveram uma necessidade relevante
> através do app."

Outra:

> "Número de necessidades relevantes resolvidas sem atendimento humano."

Outra:

> "Percepção de valor da assinatura."

------------------------------------------------------------------------

# 19. Métricas possíveis

## Engajamento

-   MAU;
-   WAU;
-   frequência de uso;
-   usuários recorrentes;
-   sessões por usuário.

## Qualidade do engajamento

-   ações concluídas;
-   funcionalidades utilizadas;
-   resolução de necessidades;
-   interações com valor.

## Atendimento

-   contatos evitáveis;
-   resolução digital;
-   redução de chamadas;
-   redução de chats.

## Relacionamento

-   NPS;
-   percepção de valor;
-   retenção;
-   renovação;
-   indicação.

## Benefícios

-   visualizações;
-   cliques;
-   utilização;
-   recorrência.

## Manutenção

-   agendamentos digitais;
-   antecedência do agendamento;
-   redução de atrasos.

------------------------------------------------------------------------

# 20. Métrica norteadora

Uma possibilidade:

# Valuable Monthly Users --- VMU

Definição proposta:

> Percentual de clientes que utilizaram o app para realizar pelo menos
> uma ação considerada de valor durante o mês.

Exemplos:

-   resolver manutenção;
-   consultar situação relevante;
-   utilizar benefício;
-   antecipar uma necessidade;
-   realizar ação relacionada à mobilidade.

Isso é uma **proposta**, não uma métrica oficial da Localiza.

------------------------------------------------------------------------

# 21. Segunda métrica importante

# Digital Resolution Rate

Percentual de necessidades elegíveis que foram resolvidas digitalmente
sem atendimento humano.

Isso conecta diretamente:

**produto → cliente → eficiência operacional.**

------------------------------------------------------------------------

# 22. Terceira métrica

# Contextual Action Rate

Percentual de recomendações contextuais que resultam em uma ação.

Exemplo:

``` text
10.000 recomendações
↓
2.000 ações
↓
20% contextual action rate
```

Não devemos definir uma meta sem dados históricos.

------------------------------------------------------------------------

# 23. IA --- arquitetura correta

## Dados

``` text
Contrato
   +
Carro
   +
KM
   +
Manutenção
   +
Localização*
   +
Histórico
   +
Preferências
```

\* somente se disponível e permitido.

↓

## Context Engine

Determina:

> "Qual é o contexto?"

↓

## Recommendation Engine

Determina:

> "O que poderia ajudar?"

↓

## IA

Determina:

> "Como comunicar/personalizar?"

↓

## Ação

``` text
Agendar
Consultar
Utilizar
Planejar
Resolver
```

------------------------------------------------------------------------

# 24. Onde NÃO usar IA

Não usar IA para:

-   cálculo financeiro;
-   regras contratuais;
-   cobrança;
-   limites de KM;
-   elegibilidade;
-   informações legais;
-   decisões críticas;
-   dados que precisam ser exatamente determinísticos.

A IA deve atuar principalmente em:

-   interpretação;
-   personalização;
-   classificação;
-   priorização;
-   linguagem;
-   recomendação.

------------------------------------------------------------------------

# 25. Privacidade

Qualquer proposta baseada em personalização deve considerar:

-   consentimento;
-   finalidade;
-   minimização de dados;
-   transparência;
-   controle do usuário;
-   segurança;
-   possibilidade de desativar personalizações sensíveis.

Especialmente no caso de:

-   localização;
-   comportamento;
-   histórico;
-   telemetria.

------------------------------------------------------------------------

# 26. Arquitetura conceitual

``` text
                  APP LOCALIZA
                       │
                       ▼
              ┌─────────────────┐
              │ Context Engine  │
              └────────┬────────┘
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
   Contrato          Veículo          Usuário
       │               │                │
       └───────────────┼────────────────┘
                       ↓
             ┌──────────────────┐
             │ Recommendation   │
             │ Engine            │
             └─────────┬────────┘
                       │
                ┌──────┴──────┐
                ↓             ↓
             Regras           IA
                │             │
                └──────┬──────┘
                       ↓
               PRÓXIMA AÇÃO
                       │
        ┌──────────────┼───────────────┐
        ↓              ↓               ↓
    Manutenção      Benefício       Suporte
        │              │               │
        └──────────────┼───────────────┘
                       ↓
                    VALOR
                       ↓
                    HÁBITO
```

------------------------------------------------------------------------

# 27. Dependências

## Dados existentes

O Case já demonstra a existência de informações relacionadas a:

-   contrato;
-   KM;
-   manutenção;
-   multas;
-   telemetria/localização;
-   combustível/bateria;
-   benefícios;
-   pagamentos.

## Dados que podem ser necessários

HIPÓTESE:

-   localização em tempo real;
-   histórico de navegação;
-   rotina;
-   preferências;
-   calendário;
-   viagens.

Não devemos assumir que todos estão disponíveis.

------------------------------------------------------------------------

# 28. Estratégia de MVP

Não tentar construir tudo.

## MVP 1

### Contexto + Proactive Care

Começar com dados que já existem.

Exemplo:

``` text
KM
Manutenção
Contrato
Fatura
Multas
```

Gerar recomendações.

## MVP 2

Adicionar:

-   benefícios contextuais;
-   personalização;
-   resolução digital.

## MVP 3

Adicionar:

-   contexto externo;
-   planejamento;
-   IA mais avançada.

------------------------------------------------------------------------

# 29. O que construir para o hackathon

Como o grupo provavelmente não terá um backend funcional completo, o
protótipo pode ser composto por:

## Tela 1 --- Home atual

Mostrar o estado atual.

------------------------------------------------------------------------

## Tela 2 --- Home futura

Mostrar a transformação:

> "Bom dia. Aqui está o que importa para você hoje."

------------------------------------------------------------------------

## Tela 3 --- Card proativo

Exemplo:

> "Sua revisão está próxima."

------------------------------------------------------------------------

## Tela 4 --- Ação

Agendamento.

------------------------------------------------------------------------

## Tela 5 --- Benefício contextual

> "Encontramos 3 benefícios relevantes para você."

------------------------------------------------------------------------

## Tela 6 --- Assistente

> "Vou viajar amanhã."

Sistema entende contexto.

------------------------------------------------------------------------

## Tela 7 --- Resumo

> "Tudo certo para sua viagem."

------------------------------------------------------------------------

# 30. Storyboard de 60--90 segundos

## Cena 1

Pessoa entra no carro.

> "Hoje eu preciso fazer minha revisão."

------------------------------------------------------------------------

## Cena 2

App envia:

> "Sua revisão está próxima."

------------------------------------------------------------------------

## Cena 3

Cliente toca.

> "Agendar revisão."

------------------------------------------------------------------------

## Cena 4

Depois:

> "Você tem um benefício de estacionamento próximo."

------------------------------------------------------------------------

## Cena 5

Sexta-feira:

> "Vai viajar?"

------------------------------------------------------------------------

## Cena 6

App:

> "Seu contrato, KM e manutenção estão em dia."

------------------------------------------------------------------------

## Cena 7

Mensagem final:

> **"Antes o cliente abria o app quando precisava da Localiza. Agora a
> Localiza aparece quando pode ajudar o cliente."**

------------------------------------------------------------------------

# 31. Comparação antes/depois

## Hoje

``` text
PROBLEMA
   ↓
CLIENTE LEMBRA
   ↓
ABRE APP
   ↓
PROCURA
   ↓
RESOLVE
   ↓
SAI
```

## Proposta

``` text
CONTEXTO
   ↓
LOCALIZA IDENTIFICA
   ↓
LOCALIZA ANTECIPA
   ↓
CLIENTE RECEBE
   ↓
AÇÃO
   ↓
VALOR
```

------------------------------------------------------------------------

# 32. Como não cair em uma solução genérica

Evitar:

-   "chatbot com IA";
-   "assistente virtual";
-   "app personalizado";
-   "feed de conteúdo";
-   "gamificação";
-   "notificações inteligentes";
-   "dashboard inteligente".

Tudo isso é apenas tecnologia.

A solução precisa responder:

> **qual necessidade concreta do motorista está sendo resolvida?**

------------------------------------------------------------------------

# 33. Teste de qualidade para cada funcionalidade

Antes de colocar qualquer recurso no protótipo:

### Pergunta 1

Isso resolve uma dor real?

### Pergunta 2

Por que precisa estar no app da Localiza?

### Pergunta 3

Por que o cliente usaria?

### Pergunta 4

Existe dado suficiente?

### Pergunta 5

A ação pode ser concluída?

### Pergunta 6

Isso gera valor para a Localiza?

### Pergunta 7

Isso pode ser escalado?

Se a resposta for "não" para várias delas, retirar.

------------------------------------------------------------------------

# 34. Por que o app da Localiza tem uma vantagem estrutural

A Localiza não é somente um aplicativo.

Ela possui:

-   frota;
-   veículos;
-   manutenção;
-   oficinas;
-   assistência;
-   contratos;
-   benefícios;
-   relacionamento;
-   atendimento;
-   infraestrutura física;
-   conhecimento da jornada.

Portanto:

> **o diferencial não deve ser construir um app melhor que outros
> apps.**

Deve ser:

> **usar o ecossistema Localiza para oferecer uma experiência que um app
> genérico de mobilidade não conseguiria oferecer.**

------------------------------------------------------------------------

# 35. Oportunidade de diferenciação

Um aplicativo de fabricante pode conhecer o carro.

Um aplicativo de estacionamento conhece estacionamento.

Um aplicativo de navegação conhece deslocamento.

Um aplicativo de benefícios conhece promoções.

A Localiza Assinatura pode conectar:

**carro + contrato + manutenção + assistência + benefícios +
mobilidade.**

Essa combinação pode ser o verdadeiro diferencial.

------------------------------------------------------------------------

# 36. Hipótese estratégica central

> **A Localiza tem informações suficientes sobre a jornada contratual
> para antecipar necessidades que hoje o cliente precisa descobrir
> sozinho.**

Isso precisa ser validado tecnicamente.

Não apresentar como fato.

------------------------------------------------------------------------

# 37. Hipótese de produto

> Quanto mais o app conseguir transformar informações já existentes em
> ações relevantes, menos ele precisará depender de novas
> funcionalidades isoladas para gerar recorrência.

------------------------------------------------------------------------

# 38. Hipótese de negócio

> Aumentar relevância digital pode fortalecer a percepção de valor da
> assinatura e reduzir necessidades de atendimento humano, mas a relação
> causal com renovação precisa ser validada.

------------------------------------------------------------------------

# 39. Possível proposta final

## Nome

**Localiza Companion**

## Tagline

> **A Localiza um passo à frente da sua rotina.**

## Problema

O app é bem avaliado e possui alta adesão, mas sua utilização é
predominantemente reativa.

## Insight

A rotina do motorista é contínua; o relacionamento digital não precisa
ser.

## Solução

Uma camada de inteligência contextual que identifica o momento do
cliente e apresenta a próxima ação relevante.

## Diferencial

Integração entre:

-   carro;
-   contrato;
-   manutenção;
-   KM;
-   benefícios;
-   suporte;
-   contexto.

## IA

Personalização e recomendação.

## MVP

Proactive Care + Home contextual + ações existentes.

------------------------------------------------------------------------

# 40. Critérios oficiais do RUPTURA

O Manual apresenta seis critérios:

1.  **Inovação**
2.  **Escalabilidade**
3.  **Coerência**
4.  **Desejabilidade**
5.  **Viabilidade**
6.  **Apresentação**

Cada um utiliza escala:

-   1 --- insuficiente;
-   2 --- regular;
-   3 --- excelente.

------------------------------------------------------------------------

# 41. Como nossa solução pode atender cada critério

## Inovação

Não criar simplesmente mais funcionalidades.

Criar uma nova lógica de relacionamento:

> **contexto → antecipação → ação.**

## Escalabilidade

O motor de contexto pode ser aplicado a milhares de clientes.

## Coerência

A solução nasce diretamente da jornada atual apresentada pela Localiza.

## Desejabilidade

O cliente recebe ajuda relevante sem precisar procurar.

## Viabilidade

Começar utilizando dados e funcionalidades que já existem.

## Apresentação

A transformação é visualmente muito simples:

**ANTES → DEPOIS**

------------------------------------------------------------------------

# 42. Riscos da solução

## Risco 1 --- Notificação excessiva

### Mitigação

Limite de frequência + relevância.

------------------------------------------------------------------------

## Risco 2 --- Personalização errada

### Mitigação

Começar com regras determinísticas.

------------------------------------------------------------------------

## Risco 3 --- Privacidade

### Mitigação

Consentimento e minimização de dados.

------------------------------------------------------------------------

## Risco 4 --- App virar um "feed"

### Mitigação

Toda recomendação precisa levar a uma ação.

------------------------------------------------------------------------

## Risco 5 --- Criar funcionalidades demais

### Mitigação

Começar com poucas jornadas de alto valor.

------------------------------------------------------------------------

## Risco 6 --- IA virar marketing

### Mitigação

Definir exatamente:

**dado → decisão → ação → benefício.**

------------------------------------------------------------------------

# 43. Perguntas difíceis da banca

## Produto

### 1. Por que o cliente abriria mais o app?

Não queremos simplesmente mais aberturas. Queremos mais necessidades
relevantes resolvidas digitalmente.

### 2. Por que isso é diferente de uma notificação push?

Porque a notificação é apenas o canal. A proposta é um motor de contexto
que identifica a necessidade e permite executar a ação.

### 3. Por que não colocar tudo na home?

Porque informação sem contexto aumenta complexidade. A home deve
priorizar o que é relevante.

------------------------------------------------------------------------

## Negócio

### 4. Como isso gera dinheiro?

Pode aumentar percepção de valor, relacionamento, uso de benefícios e
retenção, além de reduzir contatos evitáveis. Cada hipótese deve ser
validada com experimento.

### 5. Como provar impacto?

Teste A/B ou piloto controlado comparando grupos.

------------------------------------------------------------------------

## Tecnologia

### 6. Por que IA?

Para interpretar contexto e personalizar recomendações.

### 7. O que pode ser feito sem IA?

A maior parte das regras iniciais.

### 8. E se a IA errar?

Ações críticas permanecem baseadas em regras determinísticas e dados
estruturados.

------------------------------------------------------------------------

## Dados

### 9. Vocês têm todos esses dados?

Não sabemos. O Case demonstra a existência de diversos dados, mas dados
adicionais precisam ser validados.

### 10. Vocês precisam de localização?

Não necessariamente para o MVP.

------------------------------------------------------------------------

## Privacidade

### 11. Vocês vão rastrear o cliente?

Não é necessário para validar a proposta. Recursos baseados em
localização devem depender de consentimento.

------------------------------------------------------------------------

## Implementação

### 12. Quanto tempo para construir?

O MVP pode começar com poucas regras e serviços já existentes.

### 13. Precisa refazer o app?

Não necessariamente. Pode ser uma evolução da experiência existente.

------------------------------------------------------------------------

## Adoção

### 14. E se o cliente ignorar notificações?

O sistema deve priorizar poucas mensagens de alto valor.

### 15. Como criar hábito?

Não através de gamificação artificial, mas através de utilidade
recorrente.

------------------------------------------------------------------------

## Concorrência

### 16. Por que o cliente não usaria Google Maps ou Waze?

Porque esses produtos resolvem mobilidade geral. A Localiza conhece o
contrato, o veículo e os serviços específicos da assinatura.

------------------------------------------------------------------------

## Estratégia

### 17. O app não deveria fazer tudo?

Não. Ele deve fazer melhor aquilo em que a Localiza possui vantagem.

------------------------------------------------------------------------

## IA

### 18. Onde está a IA de verdade?

No entendimento de contexto e personalização, não em uma caixa de chat
genérica.

------------------------------------------------------------------------

## Métricas

### 19. Aumentar acessos é suficiente?

Não. O próprio Case alerta que o objetivo não é simplesmente aumentar
acessos sem valor claro.

------------------------------------------------------------------------

## MVP

### 20. Qual funcionalidade vocês fariam primeiro?

**Proactive Care**, começando por necessidades já suportadas por dados
existentes, como manutenção, KM, contrato e outras informações
operacionais.

------------------------------------------------------------------------

# 44. Experimento recomendado

Antes de lançar tudo:

## Grupo A

App atual.

## Grupo B

App com:

-   home contextual;
-   recomendações proativas;
-   CTA de ação.

Comparar:

-   resolução digital;
-   frequência;
-   satisfação;
-   contatos;
-   utilização de serviços;
-   retenção.

------------------------------------------------------------------------

# 45. Roadmap

## Fase 0 --- Descoberta

-   mapear dados;
-   entrevistar clientes;
-   identificar principais necessidades;
-   definir eventos.

## Fase 1 --- Regras

-   manutenção;
-   KM;
-   contrato;
-   pagamentos;
-   documentos.

## Fase 2 --- Personalização

-   preferências;
-   benefícios;
-   contexto.

## Fase 3 --- IA

-   classificação;
-   recomendação;
-   linguagem.

## Fase 4 --- Ecossistema

-   parceiros;
-   mobilidade;
-   serviços externos.

------------------------------------------------------------------------

# 46. Slide principal da solução

Uma tela deveria conter apenas:

# O app não precisa de mais funcionalidades.

## Precisa de mais contexto.

``` text
HOJE

Cliente precisa
     ↓
Abre app
     ↓
Procura
     ↓
Resolve
     ↓
Sai


AMANHÃ

Contexto
     ↓
Localiza antecipa
     ↓
Cliente recebe
     ↓
Resolve
     ↓
Percebe valor
```

------------------------------------------------------------------------

# 47. Pitch conceitual

## 0:00--0:20 --- Problema

> "Hoje, o cliente abre o app Localiza Assinatura quando precisa
> resolver alguma coisa. Ele resolve e fecha. O próprio Case mostra que
> essa relação ainda é predominantemente reativa."

## 0:20--0:50 --- Evidência

> "Mais de 80% dos clientes acessam mensalmente e o app tem NPS 84. Ou
> seja: não estamos tentando salvar um aplicativo ruim. Estamos tentando
> aproveitar um produto que o cliente já valoriza."

## 0:50--1:20 --- Insight

> "A rotina de mobilidade acontece todos os dias. O app, porém, aparece
> principalmente quando existe um problema. Nossa oportunidade é
> inverter isso."

## 1:20--2:10 --- Solução

> "Criamos uma camada de inteligência contextual. Ela entende o momento
> do cliente, identifica uma necessidade e apresenta uma ação
> relevante."

Mostrar:

-   manutenção;
-   KM;
-   benefício;
-   viagem;
-   contrato.

## 2:10--2:40 --- Tecnologia

> "Começamos com regras determinísticas usando dados que já existem. IA
> entra onde realmente agrega: interpretar contexto, personalizar e
> priorizar."

## 2:40--3:00 --- Fechamento

> **"Hoje o cliente abre o app quando precisa da Localiza. Nossa
> proposta é fazer a Localiza aparecer quando o cliente precisar
> dela."**

------------------------------------------------------------------------

# 48. Frase central da equipe

Uma boa frase para guiar todas as decisões:

> # "Não queremos mais acessos. Queremos mais momentos de valor."

------------------------------------------------------------------------

# 49. Outra opção de posicionamento

> **"De canal de atendimento para camada de inteligência da
> mobilidade."**

Essa frase pode funcionar melhor em uma apresentação mais executiva.

------------------------------------------------------------------------

# 50. Checklist final da equipe

## Problema

-   [ ] Conseguimos explicar o problema em uma frase?
-   [ ] Usamos dados reais?
-   [ ] Não confundimos inferência com fato?

## Produto

-   [ ] A solução resolve uma necessidade concreta?
-   [ ] Existe motivo para o cliente usar?
-   [ ] A Localiza possui vantagem para executar?

## Tecnologia

-   [ ] Sabemos quais dados entram?
-   [ ] Sabemos qual decisão é tomada?
-   [ ] Sabemos onde IA é necessária?
-   [ ] Sabemos onde IA não é necessária?

## Viabilidade

-   [ ] Existe MVP?
-   [ ] Sabemos o que já existe?
-   [ ] Identificamos dependências?
-   [ ] Identificamos hipóteses?

## Escalabilidade

-   [ ] O sistema funciona para milhares de clientes?
-   [ ] O custo não cresce proporcionalmente?

## UX

-   [ ] A jornada é simples?
-   [ ] Cada recomendação tem ação?
-   [ ] O cliente entende por que recebeu aquilo?

## Pitch

-   [ ] Problema em 20 segundos?
-   [ ] Dados em 30 segundos?
-   [ ] Insight claro?
-   [ ] Solução visual?
-   [ ] Tecnologia explicada?
-   [ ] Impacto?
-   [ ] Fechamento memorável?

------------------------------------------------------------------------

# 51. Resumo das melhores ideias

  -------------------------------------------------------------------------------
  Ideia          Problema       Tecnologia       IA             Valor
  -------------- -------------- ---------------- -------------- -----------------
  Mobility Home  Home pouco     Context engine   Sim            Personalização
                 contextual                                     

  Proactive Care Relação        Regras/eventos   Sim            Antecipação
                 reativa                                        

  Mobility       Rotina         Integrações      Sim            Planejamento
  Planner        fragmentada                                    

  Benefícios     Benefícios     Recomendação     Sim            Utilização
  Contextuais    pouco                                          
                 relevantes                                     

  Subscription   Valor          Analytics        Opcional       Percepção
  Value          invisível                                      

  Mobility       Baixa          Gamificação      Opcional       Hábito
  Missions       recorrência                                    

  Renewal        Relação        CRM              Sim            Retenção
  Companion      concentrada na                                 
                 renovação                                      

  Assistente     Descoberta     NLP              Sim            Acesso
                 difícil                                        

  Mobility Score Falta de visão Analytics        Opcional       Clareza
                 consolidada                                    

  Zero Surpresa  Imprevistos    Regras + alertas Opcional       Previsibilidade
  -------------------------------------------------------------------------------

------------------------------------------------------------------------

# 52. Minha linha recomendada para o grupo

Não apresentaria as 10 ideias.

Isso dilui o projeto.

Eu apresentaria:

# **PROACTIVE CARE**

### dentro de uma nova experiência de **Mobility Home**

A lógica seria:

``` text
             MOBILITY HOME
                   │
                   ▼
           CONTEXTO DO CLIENTE
                   │
                   ▼
            PROACTIVE CARE
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   Manutenção      KM       Benefícios
       │           │           │
       └───────────┼───────────┘
                   ▼
                 AÇÃO
                   ▼
                 VALOR
                   ▼
                HÁBITO
```

Isso é suficientemente concreto para o pitch e suficientemente amplo
para demonstrar visão de produto.

------------------------------------------------------------------------

# 53. O que eu deixaria como evolução

Depois do MVP:

1.  planejamento de mobilidade;
2.  benefícios contextuais avançados;
3.  assistente conversacional;
4.  personalização mais profunda;
5.  integração com parceiros;
6.  contexto de localização;
7.  IA generativa.

Assim a equipe demonstra:

> **MVP simples → evolução escalável**

em vez de:

> "Construímos uma superplataforma de IA."

------------------------------------------------------------------------

# 54. Regra de ouro

Toda funcionalidade deve passar por:

``` text
DADO
 ↓
CONTEXTO
 ↓
NECESSIDADE
 ↓
AÇÃO
 ↓
VALOR
```

Se não houver uma ação ou valor claro, a funcionalidade provavelmente
não precisa existir.

------------------------------------------------------------------------

# 55. Conclusão

O Case 2 não pede que vocês criem um aplicativo com dezenas de
funcionalidades.

Ele pede uma mudança de comportamento:

``` text
ANTES

APP = lugar para resolver problemas


DEPOIS

APP = lugar onde a Localiza ajuda
      o cliente a cuidar da sua mobilidade
```

O ativo mais interessante da Localiza não é simplesmente o aplicativo.

É a combinação:

> **cliente + carro + contrato + KM + manutenção + assistência +
> benefícios + operação + relacionamento.**

O desafio é transformar esse conjunto de informações e serviços em uma
experiência contextual.

A proposta mais forte, portanto, é:

# **fazer o app parar de esperar o cliente ter uma necessidade e começar a reconhecer momentos em que pode gerar valor.**

------------------------------------------------------------------------

## Fontes oficiais consultadas na pesquisa externa

1.  Localiza Assinatura --- página principal\
    https://assinatura.localiza.com/

2.  Localiza Assinatura --- aplicativo Google Play\
    https://play.google.com/store/apps/details?id=com.localiza.meoo.app

3.  Localiza Assinatura --- aplicativo App Store\
    https://apps.apple.com/br/app/localiza-assinatura-meoo/id1528537131

4.  Localiza Assinatura --- Clube de Benefícios\
    https://assinatura.localiza.com/clube-de-beneficios/

5.  Localiza Assinatura --- carros por assinatura\
    https://assinatura.localiza.com/assinatura

6.  Localiza Assinatura --- blog\
    https://assinatura.localiza.com/blog/

------------------------------------------------------------------------

## Documentos do RUPTURA utilizados

-   **Manual do Participante RUPTURA 2026**
-   **Cases Meoo / Localiza --- Apresentação dos Cases**
-   Material específico do **Case 2 --- Engajamento Digital / Do
    atendimento ao hábito**

**Observação final:** informações sobre o funcionamento atual do
aplicativo foram verificadas em fontes oficiais disponíveis em outubro
de 2026. Funcionalidades, telas, integrações e dados internos não
publicados oficialmente devem ser tratados como hipóteses até validação
com a Localiza.
