const socket = io();

socket.on("resp", data => {
    console.log(data.message); // Connected
});

socket.on("status_change", data => {
    console.log(data.username + " is " + data.status); // User online status changes
});

socket.on("New_user_joined", data => {
    console.log(data.message); // New user joined the room
});

socket.on("joined_room", data => {
    console.log(data.username + " joined " + data.room); // User joined a room
});

socket.on("New_group_Message", data => {
    console.log(data.message); // Room not found
});

socket.on("disconnected", data => {
    console.log(data.message); // Disconnected
});
