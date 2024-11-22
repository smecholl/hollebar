// navbar.js
document.addEventListener('DOMContentLoaded', function() {
    let pathToRoot = '';
    const pathDepth = window.location.pathname.split('/').length - 2;
  
    for (let i = 0; i < pathDepth; i++) {
      pathToRoot += '../';
    }
  
    fetch(pathToRoot + 'navbar.html')
      .then(response => response.text())
      .then(data => {
        document.getElementById('navbar-placeholder').innerHTML = data;
      });
  });
  