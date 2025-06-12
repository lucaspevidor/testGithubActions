from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "https://consulta.trf4.jus.br/trf4/controlador.php?acao=consulta_processual_valida_pesquisa&txtOrigemPesquisa=1&seq=&selForma=NU&txtValor=5039294-34.2024.4.04.7000&txtChave=&selOrigem=PR&txtDataFase=01%2F01%2F1970"
    # sb.uc_open_with_reconnect(url, reconnect_time=20)
    sb.activate_cdp_mode(url)
    sb.sleep(8)
    sb.save_screenshot("captcha_to_solve.png", "screenshots")
    captchaRect = sb.cdp.get_gui_element_rect("div.cf-turnstile")
    x = captchaRect["x"] + (captchaRect["height"] / 2) + 15
    y = captchaRect["y"] + (captchaRect["height"] / 2) - 20
    print(f"Captcha rect: {captchaRect}")
    print(f"Clicking at coordinates: ({x}, {y})")
    sb.cdp.gui_click_x_y(x, y)
    print("Clicking on the captcha...")
    # sb.uc_gui_click_captcha()
    sb.save_screenshot("captcha_clicked.png", "screenshots")
    print("Captcha clicked, waiting for it to be solved...")
    # sb.assert_element("img#captcha-success", timeout=3)
    # sb.set_messenger_theme(location="top_left")
    # sb.post_message("SeleniumBase wasn't detected", duration=3)
    sb.sleep(8)
    sb.save_screenshot("captcha_solved.png", "screenshots")
