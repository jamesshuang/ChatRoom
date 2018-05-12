var timeout = 1000;
var timeoutID = window.setTimeout(poller, timeout);

function makePost() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	var message = document.getElementById("new_message").value
	httpRequest.onreadystatechange = function() { handlePost(httpRequest, message) };

	httpRequest.open("POST", "/<roomname>", false);
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var send = "message=" + message;

	httpRequest.send(send);
}

function handlePost(httpRequest, message) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			createNode(message);
			document.getElementById("new_message").value = "";
		} else {
			alert("There was a problem with the post request.");
		}
	}
}

function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) };
	httpRequest.open("GET", "/new_messages");
	httpRequest.send();
}

function createNode(message) {
  if (document.getElementById('no_mess') !== null) {
    var remove = document.getElementById('no_mess');
    remove.parentNode.removeChild(remove);
    var li = document.getElementById('no_mess_li');
    li.parentNode.removeChild(li);
  }
  var parent = document.getElementById("messages");
  var newChild = document.createTextNode(message);
  var space = document.createElement("br");
  parent.appendChild(newChild);
  parent.appendChild(space);
}
function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			var new_messages = JSON.parse(httpRequest.responseText);
			for (var i = 0; i < new_messages.length; i++) {
          createNode(new_messages[i]);
			}
			timeoutID = window.setTimeout(poller, timeout);
		} else {
			alert("There was a problem with the poll request.  you'll need to refresh the page to recieve updates again!");
		}
	}
}
