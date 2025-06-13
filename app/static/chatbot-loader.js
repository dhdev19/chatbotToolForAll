// (function () {
//   const currentScript = document.currentScript;
//   const projectId = currentScript.getAttribute("data-project");
//   const userId = currentScript.getAttribute("data-user");

//   if (!projectId || !userId) {
//     console.error("Chatbot embed error: Missing project or user ID.");
//     return;
//   }

//   const iframe = document.createElement("iframe");
//   iframe.src = `https://api.dhgenixmedia.ae/chatbot/embed?project_id=${projectId}&user_id=${userId}`;
//   iframe.width = "100%";
//   iframe.height = "500";
//   iframe.style.border = "none";
//   iframe.setAttribute("allow", "microphone;");

//   currentScript.parentNode.insertBefore(iframe, currentScript.nextSibling);
// })();


(function () {
  const currentScript = document.currentScript || (function () {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  const userId = currentScript.getAttribute('data-user');
  const projectId = currentScript.getAttribute('data-project');

  if (!userId || !projectId) {
    console.error("Chatbot loader error: Missing data-user or data-project attributes.");
    return;
  }

  // Create container
  const container = document.createElement('div');
  container.id = 'chatbot-embed-container';
  document.body.appendChild(container);

  // Fetch the chatbot embed code
  fetch(`https://api.dhgenixmedia.ae/chatbot/embed?project_id=${projectId}&user_id=${userId}`)
    .then(response => {
      if (!response.ok) throw new Error("Failed to fetch embed code");
      return response.text();
    })
    .then(html => {
      container.innerHTML = html;

      // Re-run scripts inside injected HTML
      const scripts = container.querySelectorAll("script");
      scripts.forEach(oldScript => {
        const newScript = document.createElement("script");
        if (oldScript.src) {
          newScript.src = oldScript.src;
        } else {
          newScript.textContent = oldScript.textContent;
        }
        document.body.appendChild(newScript);
      });
    })
    .catch(error => {
      console.error("Chatbot embed failed:", error);
    });
})();
