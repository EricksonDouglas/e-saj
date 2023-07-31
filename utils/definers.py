from typing import TypedDict, List, Optional


class ModelParamsTypedDict(TypedDict):
    cnpj_cpf: str


class ModelResultProcessPartsLawyer(TypedDict):
    nome: str
    tipo: str


class ModelResultProcessPart(TypedDict):
    nome: str
    tipo: str
    advogados: Optional[List[ModelResultProcessPartsLawyer]]


class ModelResultProcessMovement(TypedDict):
    data: str
    indice: int
    descricao: str
    titulo: str


class ModelResultProcessValue(TypedDict):
    moeda: str
    valor: float


class ModelResultProcessCNJ(TypedDict):
    titulo: str


class ModelResultProcessProcedural(TypedDict):
    nome: str


class ModelResultProcess(TypedDict):
    uf: str
    area: str
    juiz: str
    partes: List[ModelResultProcessPart]
    tribunal: str
    movimentos: List[ModelResultProcessMovement]
    valorCausa: ModelResultProcessValue
    assuntosCNJ: ModelResultProcessCNJ
    urlProcesso: str
    grauProcesso: int
    orgaoJulgador: str
    unidadeOrigem: str
    classeProcessual: ModelResultProcessProcedural
    dataDistribuicao: str
    numeroProcessoUnico: str


class ModelResult(TypedDict):
    input: str
    dataConsulta: str
    processos: List[ModelResultProcess]
