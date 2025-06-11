import re
from markdownify import markdownify
from seleniumbase import SB, BaseCase


class TRF4_Crawler:
    def __init__(self, identifier: str):
        self.identifier = identifier
        self._sb: BaseCase | None = None

    @property
    def sb(self):
        if self._sb is None:
            raise Exception("SeleniumBase not initialized")
        return self._sb

    def crawlTRF4(self, analyzeLastOnly: bool = False):
        url = "https://consulta.trf4.jus.br/trf4/controlador.php?acao=consulta_processual_pesquisa&strSecao=TRF"
        tribunais = [
            "SJ Paraná",
            "SJ Rio Grande do Sul",
            "SJ Santa Catarina",
            # "Tribunal Regional Federal da 4ª Região",
        ]

        with SB(uc=True, test=True) as sb:
            sb: BaseCase
            self._sb = sb
            # sb.set_window_size(1600, 811)
            primeiraInstanciaEncontrada = False
            print("Iniciando consulta no TRF4...")
            for tIndex, tribunal in enumerate(tribunais):
                if tIndex == 0:
                    sb.activate_cdp_mode(url)
                else:
                    if primeiraInstanciaEncontrada and tribunal != "Tribunal Regional Federal da 4ª Região":
                        print("Primeira instância já encontrada, continuando com o próximo tribunal...")
                        continue
                    sb.cdp.get(url)

                sb.cdp.wait_for_element_visible("input#txtValorI", timeout=20)
                sb.cdp.press_keys("input#txtValorI", self.identifier)
                sb.cdp.select_option_by_text("select#selOrigemI", tribunal)
                if tIndex > 0:
                    sb.reconnect()
                    print("driver reconnected")
                sb.cdp.click("input#botaoEnviar")
                sb.sleep(5)
                if sb.is_connected() and sb.is_alert_present():
                    print("Alert detected, accepting...")
                    sb.accept_alert()
                    print("Alert accepted")
                # sb.cdp.gui_press_key("\n")
                hasCaptcha = sb.cdp.select("html").querySelector("div.cf-turnstile")
                if hasCaptcha:
                    if sb.is_connected():
                        print("Captcha detected, disconnecting...")
                        sb.disconnect()
                        sb.cdp.reload()
                        sb.sleep(5)
                    captchaRect = sb.cdp.get_gui_element_rect("div.cf-turnstile")
                    x = captchaRect["x"] + (captchaRect["height"] / 2)
                    y = captchaRect["y"] + (captchaRect["height"] / 3)
                    # sb.cdp.gui_click_element("div.cf-turnstile")
                    print("Clicando no captcha...")
                    sb.cdp.save_screenshot("screenshots/captcha_to_solve.png")
                    sb.uc_gui_click_captcha()
                    sb.sleep(4)
                    sb.reconnect()
                    print("Captcha solved, reconnecting...")
                    sb.cdp.save_screenshot("screenshots/captcha_solved.png")
                    exit()
                    sb.cdp.click("input[name=sbmContinuar]")

                sb.sleep(3)
                if sb.is_alert_present():
                    print("Alert detected, accepting...")
                    sb.accept_alert()
                    print("Alert accepted")
                sb.disconnect()
                print("Disconnecting...")
                try:
                    print("Procurando titulo pag")
                    sb.cdp.wait_for_element_visible("span.tituloPagina", timeout=20)
                except Exception as e:
                    if "not found" in str(e):
                        pageHtml = sb.cdp.get_page_source()
                        if "Erro na exec" in pageHtml:
                            print("Erro na execução da consulta, tentando novamente...")
                            sb.cdp.reload()
                            sb.cdp.wait_for_element_visible("span.tituloPagina", timeout=20)
                    else:
                        raise e
                titleText = sb.cdp.get_text("span.tituloPagina")
                if "Resultado da Pesquisa" not in titleText:
                    print("Processo não encontrado neste tribunal")
                    continue

                # ------------ Clicar em links para exibir mais informações ------------
                primeiraInstanciaEncontrada = True
                try:
                    print("Clicando no link para exibir mais informações")
                    sb.cdp.select("html").querySelector("a[title*='todas as partes']").click()
                    sb.sleep(5)
                    sb.cdp.wait_for_element_visible("span.tituloPagina", timeout=20)
                except Exception as e:
                    if "not found" in str(e):
                        pageHtml = sb.cdp.get_page_source()
                        if "Erro na exec" in pageHtml:
                            print("Erro na execução da consulta, tentando novamente...")
                            sb.cdp.reload()
                            sb.cdp.wait_for_element_visible("span.tituloPagina", timeout=20)
                    else:
                        raise e

                try:
                    sb.cdp.select("html").querySelector("a[title*='próximos eventos']").click()
                    sb.sleep(5)
                    sb.cdp.wait_for_element_visible("span.tituloPagina", timeout=20)
                except Exception as e:
                    if "not found" in str(e):
                        pageHtml = sb.cdp.get_page_source()
                        if "Erro na exec" in pageHtml or "Bad Gateway" in pageHtml:
                            print("Erro na execução da consulta, tentando novamente...")
                            sb.cdp.reload()
                            sb.cdp.wait_for_element_visible("span.tituloPagina", timeout=20)
                        else:
                            raise e
                    else:
                        raise e

                # ------------ Coletar informações do processo ------------
                contentHtml = sb.cdp.select("div#divConteudo").get_html()

                md = markdownify(contentHtml, heading_style="ATX", strip=["img"])
                md = re.sub(r"(^ +)|( +$)", "", md, flags=re.M)  # remover whitespaces
                md = re.sub(r"\xa0", "", md)  # remover caracteres especiais
                md = re.sub("\n+", "\n", md)  # remover quebras de linha em excesso

                assuntosMatch = re.search(r"\*\*\[Assun.*\*\*\s([\s\S]+?)\s---", md, flags=re.M)
                if not assuntosMatch:
                    raise Exception("Assuntos não encontrados")
                print("Assuntos: - " + assuntosMatch.group(1).strip())

                orgaoMatch = re.search(r"\*\*[OÓoó]rg[aã]o [Jj]ul.*?\*\*(.*)$", md, flags=re.M)
                if not orgaoMatch:
                    raise Exception("Órgão não encontrado")
                print("Vara: " + orgaoMatch.group(1).strip())

                valorMatch = re.search(r"\*\*[vV]alor da [Cc]ausa.*\*\*(.*)$", md, flags=re.M)
                if not valorMatch:
                    raise Exception("Valor da causa não encontrado")
                print("Valor da causa: " + valorMatch.group(1).strip())

                polosMatch = re.search(r"\*\*\[Assunto[\s\S]*?---([\s\S]+?)---", md, flags=re.M)
                if not polosMatch:
                    raise Exception("Polos do processo não encontrados")
                print("Polos do processo: " + polosMatch.group(0).strip())

                ultimaMovimentacaoMatch = re.search(r"---\n\*\*(\d{1,2}\/\d{1,2}\/\d{4} \d{2}:\d{2})\*\* - (.*)", md, flags=re.M)
                if not ultimaMovimentacaoMatch:
                    raise Exception("Última movimentação não encontrada")
                print("Ultima mov: " + ultimaMovimentacaoMatch.group(1) + " - " + ultimaMovimentacaoMatch.group(2))

                # ------------ Coletar informações das movimentações e documentos ------------
                movimentacoesMatch = re.findall(r"\*\*((\d{1,2}\/\d{1,2}\/\d{4} \d{2}:\d{2})\*\* - (.*) -\s+\[(.*?)\]\((.*?)\))", md, flags=re.M)
                if not movimentacoesMatch:
                    raise Exception("Movimentações não encontradas")
                print(f"Total de movimentações encontradas: {len(movimentacoesMatch)}")


if __name__ == "__main__":
    TRF4_Crawler("5039294-34.2024.4.04.7000").crawlTRF4()
