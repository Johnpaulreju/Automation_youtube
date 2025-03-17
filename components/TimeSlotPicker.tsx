import React from "react";
import { FlatList, TouchableOpacity, Text, View } from "react-native";

const TIME_SLOTS = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"];

const TimeSlotPicker = ({ selectedTime, setSelectedTime }) => {
  return (
    <FlatList
      data={TIME_SLOTS}
      horizontal
      renderItem={({ item }) => (
        <TouchableOpacity
          onPress={() => setSelectedTime(item)}
          style={{
            padding: 10,
            margin: 5,
            backgroundColor: selectedTime === item ? "#4CAF50" : "#DDD",
            borderRadius: 5,
          }}
        >
          <Text>{item}</Text>
        </TouchableOpacity>
      )}
      keyExtractor={(item) => item}
    />
  );
};

export default TimeSlotPicker;
