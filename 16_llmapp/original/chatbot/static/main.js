window.onload = function() {
  const chatBox = document.getElementById('chat-box');
  if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;

  const form = document.getElementById('chat-form');
  const textarea = document.getElementById('user-input');

  if (textarea && form) {
    textarea.addEventListener('keydown', function(event) {
      if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        form.submit();
      }
    });
  }
}