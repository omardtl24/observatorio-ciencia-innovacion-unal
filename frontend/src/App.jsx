import AppRouter from "./router/AppRouter";
import NavigationInitializer from "./components/NavigationInitializer";
  
function App() {
  return (
    <>
      <NavigationInitializer />
      <AppRouter />
    </>
  );
}

export default App;