(function () {
  const currentScript = document.currentScript;
  const projectId = currentScript.getAttribute("data-project");
  const userId = currentScript.getAttribute("data-user");

  if (!projectId || !userId) {
    console.error("Chatbot embed error: Missing project or user ID.");
    return;
  }

  const iframe = document.createElement("iframe");
  iframe.src = `https://api.dhgenixmedia.ae/chatbot/embed?project_id=${projectId}&user_id=${userId}`;
  iframe.width = "100%";
  iframe.height = "500";
  iframe.style.border = "none";
  iframe.setAttribute("allow", "microphone;");

  currentScript.parentNode.insertBefore(iframe, currentScript.nextSibling);
})();
