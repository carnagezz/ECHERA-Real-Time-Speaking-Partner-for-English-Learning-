export class LoginPage {
  constructor() {
    this.emailField = "";
    this.passwordField = "";
    this._loginMsg = document.getElementById("loginMsg");
    this._regMsg = document.getElementById("regMsg");
  }
  
  
  validateInput() {
    return true;
  }
  
  showError(message) {
    if (this._loginMsg) {
      this._loginMsg.textContent = message;
    }
  }
  
  showSuccess(message) {
    if (this._loginMsg) {
      this._loginMsg.textContent = message;
    }
  }
  
  redirectToChat() {
    location.hash = "#/chat";
  }
  
  redirectToLogin() {
    location.hash = "#/login";
  }
  
  redirectToRegister() {
    location.hash = "#/register";
  }
}