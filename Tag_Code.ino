#include <SPI.h>
#include "DW1000Ranging.h"

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define TAG_ADDR "7D:00:22:EA:82:60:3B:9B"

// #define DEBUG

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define UWB_RST 27 // reset pin
#define UWB_IRQ 34 // irq pin
#define UWB_SS 21   // spi select pin

#define I2C_SDA 4
#define I2C_SCL 5

#define ANCHOR_SWITCH_DELAY 25

struct Anchor {
    uint16_t addr;
    float range;
    float dbm;
};

#define MAX_ANCHORS 10
Anchor anchors[MAX_ANCHORS];
uint8_t numAnchors = 0;

Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup() {
    Serial.begin(115200);

    Wire.begin(I2C_SDA, I2C_SCL);
    delay(1000);
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println(F("SSD1306 allocation failed"));
        for (;;); 
    }
    display.clearDisplay();

    // Initialize the configuration
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    DW1000Ranging.initCommunication(UWB_RST, UWB_SS, UWB_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);
    DW1000Ranging.useRangeFilter(true);
    DW1000Ranging.startAsTag(TAG_ADDR, DW1000.MODE_LONGDATA_RANGE_LOWPOWER);


    // Initialize anchors
    for (int i = 0; i < MAX_ANCHORS; i++) {
        anchors[i].addr = 0;
        anchors[i].range = 0.0;
        anchors[i].dbm = 0.0;
    }
}

long int runtime = 0;
long lastAnchorSwitchTime = 0;

void loop() {
    DW1000Ranging.loop();
    if ((millis() - runtime) > 1000) {
        if (millis() - lastAnchorSwitchTime >= ANCHOR_SWITCH_DELAY) {
            displayAnchors();
            lastAnchorSwitchTime = millis();
        }
        runtime = millis();
    }
}

void newRange() {
    uint16_t addr = DW1000Ranging.getDistantDevice()->getShortAddress();
    float range = DW1000Ranging.getDistantDevice()->getRange();
    float dbm = DW1000Ranging.getDistantDevice()->getRXPower();
    updateAnchor(addr, range, dbm);
}

void newDevice(DW1000Device *device) {
    uint16_t addr = device->getShortAddress();
    addAnchor(addr);
}

void inactiveDevice(DW1000Device *device) {
    uint16_t addr = device->getShortAddress();
    deleteAnchor(addr);
}

void addAnchor(uint16_t addr) {
    if (numAnchors < MAX_ANCHORS) {
        anchors[numAnchors].addr = addr;
        numAnchors++;
    }
}

void updateAnchor(uint16_t addr, float range, float dbm) {
    for (int i = 0; i < MAX_ANCHORS; i++) {
        if (anchors[i].addr == addr) {
            anchors[i].range = range;
            anchors[i].dbm = dbm;
            return;
        }
    }
}

void deleteAnchor(uint16_t addr) {
    for (int i = 0; i < MAX_ANCHORS; i++) {
        if (anchors[i].addr == addr) {
            anchors[i].addr = 0;
            anchors[i].range = 0.0;
            anchors[i].dbm = 0.0;
            numAnchors--;
            return;
        }
    }
}

void displayAnchors() {
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);

    if (numAnchors == 0) {
        display.setTextSize(2);
        display.setCursor(0, 0);
        display.println("No Anchors");
    } else {
        display.setTextSize(1);
        int y = 0;
        for (int i = 0; i < MAX_ANCHORS; i++) {
            if (anchors[i].addr != 0) {
                display.setCursor(0, y);
                display.print("Anchor ");
                display.println(anchors[i].addr, HEX);
                display.print("Range: ");
                display.print(anchors[i].range);
                display.println(" m");
                y += 20;

                Serial.print("Anchor: ");
                Serial.print(anchors[i].addr, HEX);
                Serial.print(", Range: ");
                Serial.print(anchors[i].range);
                Serial.println(" m");
            }
        }
    }

    display.display();
}
