import React, {useEffect, useState} from 'react'
import { Link } from 'react-router-dom'

export default function Inbox(){
  const [docs, setDocs] = useState([])

  useEffect(()=>{
    fetch('/documentos')
      .then(r=>r.json())
      .then(setDocs)
      .catch(console.error)
  },[])

  return (
    <div className="container">
      <h1>Inbox Financeiro</h1>
      <table>
        <thead>
          <tr><th>Tipo</th><th>Documento</th><th>Valor</th><th>Status</th><th>Confirmado em</th></tr>
        </thead>
        <tbody>
          {docs.map(d=> (
            <tr key={d.id}>
              <td>{d.tipo}</td>
              <td><Link to={`/documento/${d.id}`}>{d.numero_documento || d.id}</Link></td>
              <td>{d.valor || '-'}</td>
              <td>{d.status}</td>
              <td>{d.confirmado_em || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
