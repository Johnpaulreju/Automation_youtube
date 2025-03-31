# Automation_Youtube

## About the Project

This project automates the process of downloading a YouTube video and re-uploading it back to YouTube at a scheduled time. The frontend is built using **Expo (React Native)**, while the backend is developed using **Flask** and runs inside a Docker container.

---

## 🚀 Getting Started

### **Frontend Setup**

1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the Expo development server:
   ```sh
   npm expo start --clear
   ```
4. Press `s` to exit development mode.
5. Use the **Expo Go** app on your mobile to test the application.

---

### **Backend Setup**

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. **Build the Docker image:**
   ```sh
   docker build -t flask-youtube-app .
   ```
3. **Run the container:**
   ```sh
   docker run -p 8000:8000 \
       -v $(pwd)/token.json:/app/token.json \
       -v $(pwd)/client_secret.json:/app/client_secret.json \
       flask-youtube-app
   ```

---

## ⚠️ Important: Authentication Setup

- You **must have** `token.json` and `client_secret.json` before running the backend.
- If you **don't** have these files, follow these steps:
  1. Get `client_secret.json` from the **Google API Console**.
  2. Run the Flask app locally to authenticate:
     ```sh
     flask run --port=8000
     ```
  3. Complete the authentication in the browser.
  4. After authentication, `token.json` will be created.
  5. Use this token for subsequent Docker runs.

Now you're ready to automate YouTube uploads! 🎬🚀

---

## 📱 Building APK for Android

Since your app is built with **Expo**, you can generate an APK for free using **EAS Build (Expo Application Services)**. Here's how:

### 📌 **Step 1: Install Expo CLI and EAS CLI (If Not Installed)**

Run the following command in your terminal:

```sh
npm install -g expo-cli eas-cli
```

---

### 📌 **Step 2: Log in to Expo**

```sh
eas login
```

(If you don’t have an Expo account, create one at [expo.dev](https://expo.dev))

---

### 📌 **Step 3: Initialize EAS in Your Project**

In your project folder, run:

```sh
eas init
```

It will create an `eas.json` file.

---

### 📌 **Step 4: Build the APK**

Run the following command:

```sh
eas build -p android --profile preview
```

This will generate an **APK** that can be installed on Android devices.

🚨 **Important:**

- If your project uses **managed workflow**, Expo will handle everything.
- If your project uses **bare workflow**, make sure you have `android` set up properly.

---

### 📌 **Step 5: Download the APK**

Once the build is complete, Expo will provide a **download link** in the terminal.

OR, to list your builds:

```sh
eas build:list
```

---

### 📌 **Step 6: Install the APK on Your Android Device**

1. Download the APK from the link.
2. Transfer it to your phone.
3. Install and test your app! 🎉

---

Let me know if you hit any issues! 🚀
