// import Nevow.Athena

Alerts = {};

Alerts.AlertWidget = Nevow.Athena.Widget.subclass('Alerts.AlertWidget');

Alerts.AlertWidget.methods(
    function __init__(self,node) {
        Alerts.AlertWidget.upcall(self, '__init__', node);
        self.fadeInItems = [];
        self.fadeTimer = null;
        self.fadeSteps = 50;
        self.timeStep = 50;
    },

    function serviceFadeInItems(self) {
        var newColorValue;

        if (self.fadeInItems.length == 0) {
            clearInterval(self.fadeTimer); //Stop the fadeIn timer.
            return;
        }
        for (var i=self.fadeInItems.length-1; i >= 0; i--) {
            var item = self.fadeInItems[i][0];
            var targetRGBvals = self.fadeInItems[i][1];
            var currentRGBvals = self.fadeInItems[i][2];
            var RGBSteps = self.fadeInItems[i][3];

            for (var c=0; c < 3; c++) {
                newColorValue = currentRGBvals[c] - RGBSteps[c];

                if (newColorValue <= targetRGBvals[c]) {
                    currentRGBvals[c] = targetRGBvals[c];
                } else {
                    currentRGBvals[c] = Math.floor(newColorValue);
                }
            }
            if (currentRGBvals[0] == targetRGBvals[0]
                    && currentRGBvals[1] == targetRGBvals[1]
                    && currentRGBvals[2] == targetRGBvals[2])
            {
                self.fadeInItems.splice(i,1);
            }
            item.style.backgroundColor = "rgb("+currentRGBvals.join(",")+")";
        }
    },

    function addRow(self, eventID) {
        var table = self.nodeById('colorTableId');
        var designated_chan = window.location.search.substring(1,100000000);
        console.debug('designated channel name:' +designated_chan);
        var EEE = eval(eventID);
        var chan = EEE[0];
        var msg = EEE[1];
        console.debug('actual channel name:' +chan);
        console.debug("actual message:");
        if (chan==designated_chan){
            console.debug('matches');
            var newRow = table.insertRow(-1);
            newRow.insertCell(0).innerHTML = '<b>'+chan+'</b>: '+msg;
            return eventID;
        }
        else{
            console.debug('no match.  ignoring');
            return '';}

        console.debug(msg);
    }


    );
