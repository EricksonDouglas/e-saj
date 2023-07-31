from datetime import datetime
from typing import List

from lxml.html import HtmlElement
from requests import Response

from utils.definers import (ModelResultProcessProcedural,
                            ModelResultProcessCNJ,
                            ModelResultProcessValue,
                            ModelResultProcessMovement,
                            ModelResultProcessPartsLawyer,
                            ModelResultProcessPart,
                            ModelResultProcess,
                            ModelResult)
from utils.robots import Robot


class TJSPPresenter:
    def __init__(self, items: List[Response], cnpj_cpf: str):
        self.items = items
        self.cnpj_cpf = Robot.only_digits(cnpj_cpf)

    @staticmethod
    def _get_procedural(page: HtmlElement) -> ModelResultProcessProcedural:
        return ModelResultProcessProcedural(
            nome=Robot.get_value_xpath(page, "//span[@id='classeProcesso']")
        )

    @staticmethod
    def _get_cnj(page: HtmlElement) -> ModelResultProcessCNJ:
        return ModelResultProcessCNJ(
            titulo=Robot.get_value_xpath(page, "//span[@id='assuntoProcesso']")
        )

    @staticmethod
    def _get_cause_value(page: HtmlElement) -> ModelResultProcessValue:
        money, value = Robot.get_value_xpath(
            page, "//div[@id='valorAcaoProcesso']"
        ).replace("  ", "").split(" ")
        return ModelResultProcessValue(
            moeda=money.strip(),
            valor=float(value.replace(".", "").replace(",", "."))
        )

    @staticmethod
    def _get_movements(page: HtmlElement) -> List[ModelResultProcessMovement]:
        result = []
        movements = page.xpath("//tbody[@id='tabelaTodasMovimentacoes']/tr")
        for index, movement in enumerate(movements, 1):
            result.append(
                ModelResultProcessMovement(
                    indice=index,
                    data=Robot.str_to_iso_format(
                        value=Robot.get_value_xpath(movement, "td[@class='dataMovimentacao']"), fmt="%d/%m/%Y"
                    ),
                    titulo=(
                            Robot.get_value_xpath(movement, "td[@class='descricaoMovimentacao']/a",
                                                  enable_upper=True) or
                            Robot.get_value_xpath(movement, "td[@class='descricaoMovimentacao']",
                                                  enable_upper=True)
                    ),
                    descricao=Robot.get_value_xpath(movement, "td[@class='descricaoMovimentacao']/span",
                                                    enable_upper=True)
                )
            )
        return result

    @staticmethod
    def _get_distribution_date(page: HtmlElement) -> str:
        return Robot.str_to_iso_format(
            value=Robot.get_value_xpath(page, "//div[@id='dataHoraDistribuicaoProcesso']").split(" - ")[0],
            fmt="%d/%m/%Y às %H:%M"
        )

    @staticmethod
    def _get_part_lawyers(page: HtmlElement) -> List[ModelResultProcessPartsLawyer]:
        result = []
        fmt_xpath = "td[@class='nomeParteEAdvogado']/span"
        for lawyer, name in zip(page.xpath(f"{fmt_xpath}/text()"),
                                page.xpath(f"{fmt_xpath}/following-sibling::text()")):
            result.append(
                ModelResultProcessPartsLawyer(
                    tipo=lawyer.split(":")[0],
                    nome=name.strip()
                )
            )
        return result

    @staticmethod
    def _map_type(value: str) -> str:
        return {
            "Reqte": "REQUERENTE",
            "Reqdo": "REQUERIDO",
            "Reqda": "REQUERIDA",
            "Perito": "PERITO"
        }.get(value, value.upper())

    @classmethod
    def _get_parts(cls, page: HtmlElement) -> List[ModelResultProcessPart]:
        result = []
        parts = page.xpath("//table[@id='tableTodasPartes']/tr")
        for part in parts:
            type_part_process = Robot.get_value_xpath(part, "td[@class='label']/span")
            result.append(
                ModelResultProcessPart(
                    nome=Robot.get_value_xpath(part, "td[@class='nomeParteEAdvogado']/text()"),
                    tipo=cls._map_type(type_part_process),
                    advogados=cls._get_part_lawyers(part)
                )
            )
        return result

    @classmethod
    def _get_process(cls, item: Response) -> ModelResultProcess:
        page = Robot.to_xpath(item.text)
        return ModelResultProcess(
            uf="SP",
            area=Robot.get_value_xpath(page, "//div[@id='areaProcesso']/span"),
            tribunal="TJSP",
            juiz=Robot.get_value_xpath(page, "//span[@id='juizProcesso']"),
            urlProcesso=item.url,
            grauProcesso=1,
            orgaoJulgador=Robot.get_value_xpath(page, "//span[@id='varaProcesso']"),
            unidadeOrigem=Robot.get_value_xpath(page, "//span[@id='foroProcesso']"),
            dataDistribuicao=cls._get_distribution_date(page),
            numeroProcessoUnico=Robot.only_digits(page.xpath("string(//span[@id='numeroProcesso'])")),
            classeProcessual=cls._get_procedural(page),
            assuntosCNJ=cls._get_cnj(page),
            valorCausa=cls._get_cause_value(page),
            movimentos=cls._get_movements(page),
            partes=cls._get_parts(page)
        )

    def run(self) -> ModelResult:
        process = [self._get_process(item) for item in self.items]
        return ModelResult(
            input=self.cnpj_cpf,
            dataConsulta=datetime.now().strftime("%Y-%m-%d"),
            processos=process
        )
