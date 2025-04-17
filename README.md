Taskoo :

Created a secure and scalable To-Do application using Flask and GraphQL. Integrated Keycloak for role-based access and Stripe for payment features. Enabled Pro plan users to upload images, and containerized the app using Docker for deployment flexibility.

## 🎥 Live Demo

Watch the full walkthrough of Taskoo in action:  
▶️ [Click here to watch the demo video](https://drive.google.com/file/d/1uy8UHCIkDS8G1CwsuyDaiKcZi3YKoifS/view?usp=drive_link)

> This demo includes:
> - Keycloak-based login
> - To-Do list CRUD operations
> - Dashboard walkthrough
> - Premium features preview (image upload)




## 📸 Tasko Web Application Screenshots
### 🔹 **1. Keycloak Authentication Integration**
![image](https://github.com/user-attachments/assets/cbbed5d7-3d2f-49ef-9520-838bb0877eb5)


### 🔹 **2. Taskoo Web Application – Dashboard _(Image Upload Disabled View)_**
![image](https://github.com/user-attachments/assets/c303358f-5b15-4767-97ca-949ffb345545)


### 🔹 **3. Taskoo Web Application – To-Do List View _(Image Upload Locked)_**

> This view displays the core To-Do list functionality in Taskoo. Users can **Create, Read, Update, and Delete** tasks with real-time interaction.  
> Image upload functionality is currently **restricted to premium users** and remains disabled in this version.

![image](https://github.com/user-attachments/assets/e2520e67-1778-4eff-a420-225c757e2336)

### 💳 **4. Taskoo – Stripe Payment Integration (Pro Plan)**

> Integrated **Stripe Checkout** to enable the Pro plan for Taskoo users.  
> Upon successful payment, users gain access to **image upload features** for profile pictures and task attachments.  
> This screen demonstrates the secure and user-friendly **Stripe payment flow**.

![image](https://github.com/user-attachments/assets/8802cd31-6704-4c9b-9b08-9800e852586c)

### 💳 **5. Taskoo – Payment Cancellation Screen**
> Integrated Stripe Checkout to handle payment cancellations for the Taskoo Pro plan.
> Upon payment failure or user cancellation, users see a dedicated screen that clearly informs them about the cancellation status.
> This screen demonstrates the user-friendly and secure Stripe cancellation flow.

![image](https://github.com/user-attachments/assets/edb101b4-9874-43ed-ade7-3dcc9744f4d3)


### 💳 **6. Taskoo – Stripe Payment Success (Pro Plan)**
> Integrated Stripe Checkout to confirm successful payments for the Taskoo Pro plan.
> Upon successful payment, users are greeted with a confirmation screen that grants them access to exclusive Pro features, such as image upload capabilities for profile pictures and task attachments.
> This screen demonstrates the smooth and reassuring Stripe payment success flow.
![image](https://github.com/user-attachments/assets/e65e29dd-d7c0-4b88-8e5b-c3dcf2a7f20f)



>After a successful Stripe payment for the Taskoo Pro plan, the image upload feature is unlocked for users.
>This premium feature allows users to upload profile pictures and task attachments, enhancing their experience.
>The screen demonstrates how image upload capabilities are activated post-payment, providing users with access to exclusive Pro features.
![image](https://github.com/user-attachments/assets/22aef10e-b783-47b8-8cd1-25f6de58196e)

### 💳 **8. Taskoo – Image Upload with CRUD in ToDo (Pro Plan)**
> Once the image upload feature is unlocked, users can attach images directly within their ToDo tasks.
> This allows users to visually enrich their tasks by uploading relevant images.
> Full CRUD operations (Create, Read, Update, Delete) are implemented for these images, ensuring a seamless and flexible user experience.
![image](https://github.com/user-attachments/assets/1ed4b3b6-1cbc-45e6-9ec7-1b07f1a1bf37)

### 🔒 **9. Taskoo – Secure Logout Functionality**
> Implemented a secure logout mechanism to ensure user session safety.
> As soon as the user clicks on logout, their user ID is cleared, and they are redirected to the login page.
> This ensures proper session management and prevents unauthorized access after logout.

![image](https://github.com/user-attachments/assets/7e97716e-5bf0-4224-9025-16cd8684323f)
