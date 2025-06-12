from seleniumbase import SB

canvasInject = """(function injectCanvasOnWebsite() {
    function drawCircle(event) {
        const canvas = document.getElementById("drawingCanvas");
        const ctx = canvas.getContext("2d");
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
    }

    const canvas = document.createElement("canvas");
    canvas.id = "drawingCanvas";
    canvas.style.position = "fixed";
    canvas.style.top = "0";
    canvas.style.left = "0";
    canvas.style.zIndex = "1000"; // Ensure it is on top of other elements
    canvas.style.backgroundColor = "rgba(0, 0, 0, 0.25)";
    document.body.appendChild(canvas);

    // Set canvas dimensions
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Add event listener for drawing
    canvas.addEventListener("click", drawCircle);
})()"""

with SB(uc=True, test=True) as sb:
    url = "https://seleniumbase.io/apps/turnstile"
    sb.uc_open_with_reconnect(url)
    sb.save_screenshot("captcha_to_solve.png", "screenshots")
    sb.sleep(2)
    sb.execute_script(canvasInject)
    sb.sleep(2)
    sb.save_screenshot("canvas_injected.png", "screenshots")
    sb.uc_gui_click_x_y(200, 400)
    sb.uc_gui_click_captcha()
    sb.save_screenshot("captcha_clicked.png", "screenshots")
    sb.sleep(3)
    sb.save_screenshot("captcha_solved.png", "screenshots")
    sb.save_screenshot_to_logs()