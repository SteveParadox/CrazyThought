
$(document).ready(function(){

var socket = io.connect('http://' + document.domain + ':' + location.port + '/client');
var socket_messages= io('http://' + document.domain + ':' + location.port + '/messages')


$('#send').on('click', function(){
var message =$('#messgae').val();

socket_messages.emit('message from user', message);
});

socket_messages.on('from Flask', function(msg){
    console.log(msg);
});
socket.on('server originated', function(msg){
 console.log(msg);
});


var private_socket = io('http://' + document.domain + ':' + location.port + '/private')
$('#send_username').on('click', function(){
private_socket.emit('username', $('#username').val());

});

$('#send_private_message').on('click', function(){
var recipient= $('#send_to_username').val();
var message_to_send = $('#private_message').val();
private_socket.emit('private_message', {'username': recipient, 'message': message_to_send});

});
private_socket.on('new_private_message', function(msg){
console.log(msg)

});

});
