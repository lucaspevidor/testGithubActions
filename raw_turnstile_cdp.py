from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "https://seleniumbase.io/apps/turnstile"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.assert_element("img#captcha-success", timeout=3)
    sb.set_messenger_theme(location="top_left")
    sb.post_message("SeleniumBase wasn't detected", duration=3)
    sb.save_screenshot("captcha_solved.png", "screenshots")
