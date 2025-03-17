

import React, { useState, useEffect } from "react";
import { View, Text, TextInput, FlatList, Alert, TouchableOpacity, ActivityIndicator } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import DateTimePicker from "@react-native-community/datetimepicker";
import { Button, Card, Paragraph } from "react-native-paper";
import { SafeAreaView } from "react-native-safe-area-context";
import { BlurView } from "expo-blur";

const TIME_SLOTS = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"];

export default function App() {
  const [url, setUrl] = useState("");
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedTime, setSelectedTime] = useState(TIME_SLOTS[0]);
  const [queue, setQueue] = useState([]);
  const [showPicker, setShowPicker] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => { loadQueue(); }, []);
  useEffect(() => {
    const interval = setInterval(() => {
      const currentTime = new Date();
      const updatedQueue = queue.filter(item => {
        const scheduledTime = new Date(`${item.date}T${item.time}:00`);
        return scheduledTime > currentTime;
      });
      setQueue(updatedQueue);
      saveQueue(updatedQueue);
    }, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [queue]);

  const loadQueue = async () => {
    const storedQueue = await AsyncStorage.getItem("uploadQueue");
    if (storedQueue) setQueue(JSON.parse(storedQueue));
  };

  const saveQueue = async (newQueue) => {
    await AsyncStorage.setItem("uploadQueue", JSON.stringify(newQueue));
  };

  const addToQueue = async () => {
    if (!url) {
      Alert.alert('Error', 'Please enter a YouTube URL');
      return;
    }

    setLoading(true);
    const newEntry = { url, date: selectedDate.toISOString().split('T')[0], time: selectedTime };
    
    try {
      const response = await fetch('http://192.168.0.104:8000/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: newEntry.url,
          schedule_time: `${newEntry.date} ${newEntry.time}`,
        }),
      });
      const data = await response.json();

      if (response.ok) {
        Alert.alert('Success', 'Upload scheduled successfully.');
        const updatedEntry = { ...newEntry, video_id: data.video_id };
        setQueue(prevQueue => [...prevQueue, updatedEntry]);
        saveQueue([...queue, updatedEntry]);
        setUrl('');
      } else {
        Alert.alert('Error', data.error || 'An error occurred');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to schedule upload');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const removeFromQueue = async (index) => {
    const video_id = queue[index].video_id;
    setLoading(true);
    
    try {
      const response = await fetch('http://192.168.0.104:8000/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id }),
      });
      const data = await response.json();

      if (response.ok) {
        setQueue(prevQueue => prevQueue.filter((_, i) => i !== index));
        saveQueue(queue.filter((_, i) => i !== index));
        Alert.alert('Success', 'Video deleted successfully!');
      } else {
        Alert.alert('Error', data.error);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to delete video');
    } finally {
      setLoading(false);
    }
  };

  const clearQueue = async () => {
    setQueue([]);
    await AsyncStorage.removeItem("uploadQueue");
  };

  // Calculate filtered time slots
  const currentTime = new Date();
  const isToday = selectedDate.toDateString() === currentTime.toDateString();
  const filteredTimeSlots = TIME_SLOTS.filter(time => {
    if (!isToday) return true;
    const [hours, minutes] = time.split(':').map(Number);
    const slotTime = new Date(selectedDate);
    slotTime.setHours(hours, minutes, 0, 0);
    return slotTime > currentTime;
  });

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <View style={{ padding: 20 }}>
        {loading && (
          <BlurView intensity={50} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, justifyContent: "center", alignItems: "center", zIndex: 1 }}>
            <ActivityIndicator size="large" color="#0000ff" />
          </BlurView>
        )}
        
        <Text style={{ fontSize: 20, fontWeight: "bold", marginBottom: 10 }}>YouTube Video Scheduler</Text>
        <TextInput placeholder="Paste YouTube URL" value={url} onChangeText={setUrl} style={{ borderWidth: 1, padding: 10, marginBottom: 10 }} />

        <Button mode="contained" onPress={() => setShowPicker(true)}>Select Date</Button>
        {showPicker && (
          <DateTimePicker
            value={selectedDate}
            mode="date"
            display="default"
            minimumDate={new Date()}
            maximumDate={new Date(Date.now() + 15 * 24 * 60 * 60 * 1000)}
            onChange={(event, date) => {
              setShowPicker(false);
              if (date) setSelectedDate(date);
            }}
          />
        )}
        <Text style={{ marginTop: 10 }}>Selected Date: {selectedDate.toDateString()}</Text>
        <Text>Select Time Slot:</Text>
            {filteredTimeSlots.map(time => (
                <TouchableOpacity key={time} onPress={() => setSelectedTime(time)}>
                <Text style={{ padding: 10, backgroundColor: selectedTime === time ? 'lightblue' : 'white' }}>
                    {time}
                </Text>
                </TouchableOpacity>
            ))}
            {filteredTimeSlots.length === 0 && <Text>No available time slots for today.</Text>}


        <Button mode="contained" onPress={addToQueue} style={{ marginTop: 10 }}>Schedule Upload</Button>
        <Button mode="contained" onPress={clearQueue} style={{ marginTop: 10, backgroundColor: 'red' }}>Clear Queue</Button>

        <Text style={{ fontSize: 18, fontWeight: "bold", marginTop: 20 }}>Scheduled Uploads:</Text>
        <FlatList
          data={queue}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item, index }) => (
            <Card style={{ marginVertical: 5, padding: 10 }}>
              <Paragraph>URL: {item.url}</Paragraph>
              <Paragraph>Date: {item.date}</Paragraph>
              <Paragraph>Time: {item.time}</Paragraph>
              <Button mode="outlined" onPress={() => removeFromQueue(index)}>Remove</Button>
            </Card>
          )}
        />
      </View>
    </SafeAreaView>
  );
}