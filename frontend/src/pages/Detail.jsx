import React, {useEffect, useState} from 'react'
import { useParams } from 'react-router-dom'

export default function Detail(){
  const { id } = useParams()
  const [doc, setDoc] = useState(null)

  useEffect(()=>{
    fetch(`/documentos/${id}`)
      .then(r=>r.json())
      .then(setDoc)
  },[id])

  if(!doc) return <div>Carregando...</div>

  const confirmar = () => {
    fetch(`/documentos/${id}/confirmar?usuario=system`, {method: 'POST'})
      .then(()=>alert('Marcado como FEITO'))
  }

  return (
    <div className="container">
      <h1>Documento {doc.numero_documento || doc.id}</h1>
      <div className="card">
        <p><strong>Tipo:</strong> {doc.tipo}</p>
        <p><strong>Fornecedor:</strong> {doc.fornecedor}</p>
        <p><strong>CNPJ:</strong> {doc.cnpj}</p>
        <p><strong>Valor:</strong> {doc.valor}</p>
        <p><strong>Status:</strong> {doc.status}</p>
        <button onClick={confirmar}>Marcar como FEITO</button>
      </div>

      <div className="card">
        <h3>Preview</h3>
        {doc.anexos && doc.anexos[0] && (
          <img src={`data:image/png;base64,${doc.anexos[0].preview_imagem}`} alt="preview" style={{maxWidth: '800px'}} />
        )}
      </div>

    </div>
  )
}
