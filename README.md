# 🧭 Travel Itinerary Planner - Refatoracao



> **Projeto Original:** [edgarvtt/Travel-Itinerary-Planner](https://github.com/edgarvtt/Travel-Itinerary-Planner)  
> **Versão Refatorada:** Expandida com novas funcionalidades e melhorias arquiteturais

Um aplicativo web completo para planejamento de viagens com classes POO, sistema de usuários, planejamento colaborativo e funcionalidades avançadas de recomendação e comunidade.

## 🚀 **Status do Projeto**

**⚠️ EM PROCESSO DE REFATORAÇÃO**

Este projeto está sendo refatorado e expandido. O próximo passo será implementar **padrões de projeto** para melhorar a arquitetura e manutenibilidade do código.

## 📋 **Funcionalidades Implementadas**

### ✅ **Totalmente Implementadas**

1. **✅ Criação e personalização de itinerários**
   - Sistema completo de criação de viagens
   - Adição de voos, hotéis, atividades e despesas
   - Interface web responsiva

2. **✅ Ferramentas de Planejamento Colaborativo**
   - Sistema de códigos de compartilhamento
   - Convite de colaboradores em tempo real
   - Planejamento conjunto de itinerários

3. **✅ Acompanhamento de despesas e gerenciamento de orçamento**
   - Controle detalhado de gastos por categoria
   - Cálculo automático de orçamento
   - Interface visual do orçamento

4. **✅ Sistema de Usuários e Autenticação**
   - Cadastro e login de usuários
   - Dashboard personalizado
   - Gerenciamento de sessões

5. **✅ Guias e recursos de viagem** *(NOVO)*
   - Guias culturais, gastronômicos e de transporte
   - Recursos úteis (hospitais, embaixadas, aeroportos)
   - Sistema de categorização e tags
   - API completa para gerenciamento

6. **✅ Avaliações de usuários e contribuições da comunidade** *(NOVO)*
   - Sistema de reviews e ratings
   - Contribuições da comunidade (dicas, destinos)
   - Reações (likes/dislikes) em conteúdo
   - API para gerenciamento de conteúdo colaborativo

### 🔄 **Parcialmente Implementadas - Partes que possuem dependencias externas náo foram feitas**

7. **🔄 Personalização com base nas preferências** *(NOVO - Parcialmente)*
   - Sistema de preferências do usuário
   - Perfis de viagem personalizados
   - Algoritmo básico de recomendações
   - **Limitação:** Sistema de IA avançado não implementado

8. **🔄 Acesso móvel e funcionalidade offline**
   - Interface responsiva implementada
   - **Pendente:** Funcionalidade offline

### ❌ **Não Implementadas - Funcionalidades que possuem dependencias externas**

9. **❌ Integração de reservas**
   - **Motivo:** Depende de APIs pagas externas
   - **Impacto:** Não pode ser implementado sem custos adicionais

10. **❌ Integração de mapas e planejamento de rotas**
    - **Motivo:** Depende de APIs de mapas (Google Maps, OpenStreetMap)
    - **Impacto:** Requer chaves de API e configuração externa

## 🆕 **Novas Funcionalidades Implementadas**

### **1. Sistema de Guias de Viagem**
```python
class TravelGuide(ItineraryItem):
    # Guias culturais, gastronômicos, de transporte
    # Sistema de categorização e tags
    # Conteúdo rico e estruturado
```

### **2. Sistema de Recursos Úteis**
```python
class TravelResource(ItineraryItem):
    # Hospitais, embaixadas, aeroportos
    # Informações de contato e localização
    # Recursos categorizados por tipo
```

### **3. Sistema de Avaliações e Contribuições**
```python
class Review(ItineraryItem):
    # Reviews com rating e comentários
    # Sistema de reações (likes/dislikes)
    
class UserContribution(ItineraryItem):
    # Dicas da comunidade
    # Sugestões de destinos
    # Conteúdo colaborativo
```

### **4. Sistema de Personalização**
```python
class UserPreference(ItineraryItem):
    # Preferências de clima, orçamento, interesses
    # Sistema de pesos para priorização
    
class TravelProfile(ItineraryItem):
    # Perfis de viagem personalizados
    # Estilos de viagem (cultural, aventura, etc.)
    
class Recommendation(ItineraryItem):
    # Recomendações personalizadas
    # Algoritmo básico de matching
```

## 🏗️ **Arquitetura Técnica**

### **Backend (Python/Flask)**
- **Framework:** Flask com CORS habilitado
- **Banco de Dados:** JSON persistente (`database.json`)
- **APIs:** RESTful endpoints para todas as funcionalidades
- **Classes:** 15+ classes POO com herança e polimorfismo

### **Frontend (HTML/CSS/JavaScript)**
- **Design:** Interface responsiva com Tailwind CSS
- **Páginas:** Landing page, dashboard, planner, detalhes
- **Funcionalidades:** Sistema de usuários, planejamento colaborativo

### **Padrões POO Implementados**
- **Herança:** `ItineraryItem` como classe base
- **Polimorfismo:** Duck typing com método `to_dict()`
- **Encapsulamento:** Classe `DataStore` para gerenciamento de dados
- **Classe Abstrata:** `ItineraryItem` (conceitualmente)

## 📊 **Estatísticas do Projeto**

| Métrica | Original | Refatorado | Aumento |
|---------|----------|------------|---------|
| Classes | 8 | 15+ | +87% |
| Funcionalidades | 3/10 | 6/10 | +100% |
| Linhas de Código | ~800 | ~1100+ | +37% |
| Endpoints API | 12 | 25+ | +108% |

## 🚀 **Como Usar**

### **Pré-requisitos**
```bash
# Instalar Python 3.8+
# Instalar Flask e dependências
pip install flask flask-cors
```

### **Executar o Projeto**
```bash
# 1. Clone o repositório
git clone <seu-repositorio>

# 2. Navegue para o diretório
cd Travel-Itinerary-Planner/PROJETO-POO

# 3. Execute o servidor
python app.py

# 4. Abra no navegador
# http://localhost:5000
# Abra index.html para a interface web
```

### **Estrutura do Projeto**
```
PROJETO-POO/
├── app.py              # Servidor Flask e lógica backend
├── database.json       # Banco de dados JSON
├── index.html          # Página inicial
├── dashboard.html      # Dashboard do usuário
├── login.html          # Sistema de login
├── signup.html         # Sistema de cadastro
└── trip-details.html   # Detalhes da viagem
```

## 🔄 **Próximos Passos - Padrões de Projeto**

### **1. Padrões Arquiteturais**
- **MVC (Model-View-Controller):** Separar lógica de negócio da apresentação
- **Repository Pattern:** Abstrair acesso aos dados
- **Service Layer:** Camada de serviços para lógica de negócio

### **2. Padrões de Criação**
- **Factory Method:** Para criação de diferentes tipos de itinerários
- **Builder Pattern:** Para construção complexa de viagens
- **Singleton:** Para gerenciamento de configurações

### **3. Padrões Estruturais**
- **Adapter:** Para integração com APIs externas futuras
- **Decorator:** Para adicionar funcionalidades aos objetos
- **Facade:** Para simplificar interfaces complexas

### **4. Padrões Comportamentais**
- **Observer:** Para notificações em tempo real
- **Strategy:** Para diferentes algoritmos de recomendação
- **Command:** Para operações de undo/redo

## 🤝 **Contribuição**

Este projeto está em processo de refatoração. Contribuições são bem-vindas:

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Commit** suas mudanças
4. **Push** para a branch
5. **Abra** um Pull Request

## 📝 **Changelog**

### **v2.0 - Refatoração Major**
- ✅ Implementação de 3 novas funcionalidades principais
- ✅ Sistema de guias e recursos de viagem
- ✅ Sistema de avaliações e contribuições da comunidade
- ✅ Sistema de personalização e recomendações
- ✅ Expansão de 8 para 15+ classes
- ✅ Adição de 13+ novos endpoints API
- ✅ Melhoria na documentação e estrutura do código

### **v1.0 - Projeto Original**
- ✅ Sistema básico de planejamento de viagens
- ✅ Planejamento colaborativo
- ✅ Gerenciamento de orçamento
- ✅ Interface web responsiva

## 📄 **Licença**

Este projeto é baseado no projeto original de [edgarvtt/Travel-Itinerary-Planner](https://github.com/edgarvtt/Travel-Itinerary-Planner) e está sendo refatorado para fins educacionais.

## 👨‍💻 **Autor**

**Projeto Original:** [edgarvtt](https://github.com/edgarvtt)  
**Refatoração:** [Seu Nome](https://github.com/seuusuario)

---

**⚠️ Nota:** Este projeto está em processo ativo de refatoração. A próxima versão incluirá implementação de padrões de projeto para melhorar a arquitetura e manutenibilidade do código.