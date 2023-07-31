from typing import List

from requests import Response

from presenter.tjsp import ModelResult, TJSPPresenter
from utils.definers import ModelParamsTypedDict
from utils.robots import Robot


class Bot(Robot):
    def __init__(self, params: ModelParamsTypedDict, logger):
        super().__init__(params, logger)
        self.host = "https://esaj.tjsp.jus.br"

    def _search(self) -> List[str]:
        response = self.session.get(
            url=f"{self.host}/cpopg/search.do",
            params={'conversationId': '',
                    'cbPesquisa': 'DOCPARTE',
                    'dadosConsulta.valorConsulta': self.params['cnpj_cpf'],
                    'cdForo': '-1'}
        )
        page = self.to_xpath(response.text)
        return [url for url in page.xpath("//a[@class='linkProcesso']/@href")]

    def _extract(self, path: str) -> Response:
        return self.session.get(f"{self.host}{path}")

    def run(self) -> ModelResult:
        paths_process = self._search()
        items = [self._extract(path) for path in paths_process[:2]]
        result = TJSPPresenter(items=items, cnpj_cpf=self.params['cnpj_cpf']).run()
        self.save_to_json(result, f"/tmp/result_cortex_{self.only_digits(self.params['cnpj_cpf'])}")
        return result


if __name__ == '__main__':
    import logging
    from sys import stdout
    from pprint import pprint
    from time import time
    from datetime import timedelta

    logging.basicConfig(stream=stdout, level=logging.DEBUG)
    for cnpj_cpf in []:
        start = time()
        pprint(Bot(params=ModelParamsTypedDict(cnpj_cpf=cnpj_cpf), logger=logging).run())
        print("\nExecution:", str(timedelta(seconds=time() - start)).split(".")[0])
