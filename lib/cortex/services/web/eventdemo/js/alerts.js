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

    function fadeIn(self, item, targetRGBVals) {
        var RGBSteps = [(255-targetRGBVals[0])/self.fadeSteps,(255-targetRGBVals[1])/self.fadeSteps,(255-targetRGBVals[2])/self.fadeSteps];
        var newFadeItem = [item,targetRGBVals,[255,255,255],RGBSteps];
        self.fadeInItems.push(newFadeItem); //item, targetColor, currentColor
        if (self.fadeInItems.length == 1) //If this is the only item, start the timer.
        {
            self.fadeTimer = setInterval(function () {self.serviceFadeInItems()}, self.timeStep)            
        }
    },

        
    function addRow(self, eventID) {
        var table = self.nodeById('colorTableId');
        var newRow = table.insertRow(-1);
        newRow.insertCell(0).innerHTML = eventID;
        self.fadeIn(newRow, [194,228,177]);
        return eventID;
    }


    );
