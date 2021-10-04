function raidProtection(token, data) {
	var request = new XMLHttpRequest()
	request.open("GET", `https://doge-utilities.herokuapp.com/web/api/raid-protection/${token}/${data}`)
	request.send()
	request.onreadystatechange = (e) => {
		text = request.responseText
		var currentStatus = "Enabled"
		if (text == "0") {
			currentStatus = "Disabled"
		}
		var button = document.getElementById("raid-protection-button." + data)
		button.innerHTML = "Raid Protection: " + currentStatus
	}
}
