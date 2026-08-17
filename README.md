# Medidor de Consumo

Monitor local para estimar o consumo do PC usando a potência da CPU e da GPU.
Ele grava os intervalos no SQLite e mostra um dashboard com consumo de hoje,
custo, média diária, projeção mensal e gráficos.

> É uma estimativa: CPU + GPU + 50 W extras para placa-mãe, RAM, ventoinhas,
> monitor e perdas da fonte. Não substitui uma tomada com medidor de energia.

## Requisitos

- Windows 11
- [uv](https://docs.astral.sh/uv/)
- Libre Hardware Monitor extraído no computador

## Preparação

1. Baixe o Libre Hardware Monitor pelo [repositório oficial](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases).
2. Copie as DLLs extraídas para a pasta `lib/` do projeto, incluindo
   `LibreHardwareMonitorLib.dll`.
3. Instale as dependências:

```powershell
uv sync
```

## Uso

Para iniciar o monitor:

```powershell
uv run medidor-consumo
```

Em outro terminal, abra o dashboard:

```powershell
uv run streamlit run dashboard.py
```

Ou dê dois cliques em `abrir-medidor.cmd`: ele inicia o monitor em segundo
plano e abre o dashboard em `http://localhost:8501`.

Os dados ficam somente em `data/consum.db` e não são enviados para lugar nenhum.

## Como a estimativa funciona

- A cada 2,5 segundos, o projeto lê `CPU Package` e `GPU Package`.
- Soma 50 W configuráveis em `EXTRA_POWER_W`.
- Converte watts e tempo decorrido em kWh.
- Multiplica o kWh por `PRICE_PER_KWH_BRL` para estimar o custo.

O valor padrão atual é R$ 0,82 por kWh. Ajuste as duas constantes em
`src/medidor_consumo/__init__.py` conforme o seu PC e a sua conta de luz.

## Inicialização automática

O agendador do Windows inicia somente o monitor escondido ao entrar na conta.
Como a leitura de potência pode exigir privilégios de administrador, a tarefa
`Medidor de Consumo` deve estar configurada com **Executar com privilégios mais
altos**. O dashboard continua abrindo manualmente pelo atalho quando você quiser.
