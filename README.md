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
