# Common Diagram Patterns

## Software Architecture Patterns

### 1. Microservices Architecture
```mermaid
flowchart TB
    Client[Client] --> Gateway[API Gateway]
    Gateway --> Auth[Auth Service]
    Gateway --> User[User Service]
    Gateway --> Order[Order Service]
    Gateway --> Payment[Payment Service]
    
    User --> UserDB[(User DB)]
    Order --> OrderDB[(Order DB)]
    Payment --> PaymentDB[(Payment DB)]
    
    Order -.-> Queue[Message Queue]
    Payment -.-> Queue
```

### 2. MVC Pattern
```mermaid
flowchart LR
    User[User] --> View[View]
    View --> Controller[Controller]
    Controller --> Model[Model]
    Model --> Database[(Database)]
    Model --> Controller
    Controller --> View
```

### 3. Event-Driven Architecture
```mermaid
flowchart TD
    Producer1[Producer 1] --> EventBus[Event Bus]
    Producer2[Producer 2] --> EventBus
    EventBus --> Consumer1[Consumer 1]
    EventBus --> Consumer2[Consumer 2]
    EventBus --> Consumer3[Consumer 3]
```

## Business Process Patterns

### 1. Approval Workflow
```mermaid
flowchart TD
    Start[Request Submitted] --> Review{Manager Review}
    Review -->|Approve| Finance{Finance Review}
    Review -->|Reject| Rejected[Request Rejected]
    Finance -->|Approve| Approved[Request Approved]
    Finance -->|Reject| Rejected
    Approved --> Process[Process Request]
    Process --> Complete[Complete]
```

### 2. Customer Journey
```mermaid
flowchart LR
    Awareness[Awareness] --> Interest[Interest]
    Interest --> Consideration[Consideration]
    Consideration --> Purchase[Purchase]
    Purchase --> Retention[Retention]
    Retention --> Advocacy[Advocacy]
```

## Data Flow Patterns

### 1. ETL Pipeline
```mermaid
flowchart LR
    Source1[Source 1] --> Extract[Extract]
    Source2[Source 2] --> Extract
    Extract --> Transform[Transform]
    Transform --> Load[Load]
    Load --> DataWarehouse[(Data Warehouse)]
```

### 2. Real-time Processing
```mermaid
flowchart TD
    Stream[Data Stream] --> Ingestion[Ingestion Layer]
    Ingestion --> Processing[Stream Processing]
    Processing --> Analytics[Real-time Analytics]
    Processing --> Storage[(Storage)]
    Analytics --> Dashboard[Dashboard]
```

## Development Patterns

### 1. CI/CD Pipeline
```mermaid
flowchart LR
    Code[Code] --> Build[Build]
    Build --> Test[Test]
    Test --> Deploy[Deploy]
    Deploy --> Monitor[Monitor]
    Monitor -.-> Code
```

### 2. Git Flow
```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout develop
    merge feature
    checkout main
    merge develop
```

## State Machine Patterns

### 1. Order Status
```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Processing
    Processing --> Shipped
    Processing --> Cancelled
    Shipped --> Delivered
    Delivered --> [*]
    Cancelled --> [*]
```

---
*Use these patterns as templates for your own diagrams*