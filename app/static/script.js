let msgbox = document.querySelector('.chatbox');
msgbox.scrollTop = msgbox.scrollHeight;




var blink_speed = 1000; // every 1000 == 1 second, adjust to suit
var t = setInterval(function () {
    var ele = document.getElementById('container');
    ele.style.visibility = (ele.style.visibility == 'hidden' ? '' : 'hidden');
}, blink_speed);
document.write("hello");