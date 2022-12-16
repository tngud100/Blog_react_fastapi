import React from 'react'
import { Container, Image, Navbar } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuthStore } from 'stores/RootStore'
import LogoImg from "assets/img/jaylog.png"


const MyNavbar = () => {
    const authStore = useAuthStore();
  

    return (
    <div
        class="sticky-top shadow"
        style={{ backgroundColor: "rgba(255, 255, 255, 0.95)" }}
    >
        <Navbar>
            <Container>
                <Link to={"/"} className="navbar-brand fs-3 text-dark">
                    <Image src={LogoImg} style={{height: "50px"}}></Image>
                </Link>
            </Container>
        </Navbar>

    </div>
    
    );
};

export default MyNavbar