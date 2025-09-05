'use strict';
const reminderP = document.createElement('p');
reminderP.innerHTML = 'And remember the proper name for a home page is <em>index.html</em>';
reminderP.style.cssText = `
background: #ccc;
border: 1px solid #333;
border-radius: 5px;
padding: 5px;
`;
document.querySelector('p').after(reminderP);
