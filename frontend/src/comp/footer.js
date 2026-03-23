import axios from 'axios';
import {useState } from 'react';

export default function Footer() {
  const [data,setData]=useState(
    {
      comment:''
    }
  );

  function handleChanded(a){
    setData({...data,[a.target.name]:a.target.value});
  }

  const gae=(a)=>{
    a.preventDefault();
    axios.post('http://localhost:8082/cmtinsert/',data)
    .then(res=>alert("insert Successfully"))
    .catch(err=>alert(err));
  }
  
  return (
    <>
      {/*  user comment post  */}
      <div className="row">
        <div className="col-12 fixed-bottom bg-dark border-top border-light p-2 p-md-3">
          <form onSubmit={gae} className="col-12 col-md-10 col-lg-7 mx-auto">
            <div className="input-group align-items-end">

              <textarea placeholder="Say your thoughts..." rows="1" style={{ resize: "none" }}
              className="btm form-control shadow-none bg-transparent text-info border-primary fs-6 fs-md-5 py-2 py-md-3"
              name='comment' onChange={handleChanded} value={data.comment} />

              <button className="ptm btn btn-outline-primary fw-bold  fs-6 fs-md-5 px-3 px-md-4 py-2 py-md-3">POST</button>
              
            </div>
          </form>
        </div>
      </div>

    </>
  );
}