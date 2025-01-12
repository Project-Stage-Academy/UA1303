import Navbar from '../navbar/navbar';
import Footer from '../footer/footer';
import "./layout.css";

const Layout = ({ children }) => {
  return (
    <div className="layout">
      <Navbar />
      <main className="content">{children}</main>
      <Footer />
    </div>
  );
};

export default Layout;